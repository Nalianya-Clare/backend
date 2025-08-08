from datetime import date
from django.utils import timezone
from django.db.models import Count
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from .models import (
    Category, Quiz, Question, Answer, QuizAttempt, Resource, UserAnswer,
    Badge, UserBadge, UserProgress
)
from .serializers import (
    CategorySerializer, QuizListSerializer, QuizDetailSerializer,
    QuizAttemptSerializer, ResourceSerializer, UserAnswerSerializer, BadgeSerializer,
    UserBadgeSerializer, UserProgressSerializer,
    StartQuizSerializer, SubmitAnswerSerializer,
    CreateQuizSerializer
)
from util.messages.hundle_messages import success_response, error_response


class QuizCustomView(ModelViewSet):
    """Base custom view following account app pattern"""
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTStatelessUserAuthentication]
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    def get_actual_user(self, request):
        """Get actual User instance from database to avoid TokenUser issues"""
        from account.models import User
        try:
            return User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            return None

    def create(self, request, *args, **kwargs):
        """Create resource"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response = success_response(
            status_code=status.HTTP_201_CREATED,
            message_code="create_success",
            message={"message": "Created successfully", "id": instance.id}
        )
        return Response(response, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """Get single resource"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response = success_response(
            status_code=status.HTTP_200_OK,
            message_code="get_data",
            message={"data": serializer.data}
        )
        return Response(response, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        """List resources with pagination"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            response = success_response(
                status_code=status.HTTP_200_OK,
                message_code="get_data",
                message=paginated_response.data
            )
            return Response(response, status=status.HTTP_200_OK)
        
        serializer = self.get_serializer(queryset, many=True)
        response = success_response(
            status_code=status.HTTP_200_OK,
            message_code="get_data",
            message={"data": serializer.data}
        )
        return Response(response, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """Update resource"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        response = success_response(
            status_code=status.HTTP_200_OK,
            message_code="update_success",
            message="Updated successfully"
        )
        return Response(response, status=status.HTTP_200_OK)

class ResourceViewSet(QuizCustomView):
    """Resource upload endpoints (PDF, images, text)"""
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    # http_method_names = ['post', 'get', 'head']

    def get_queryset(self):
        # Optionally filter by quiz or user if needed
        return super().get_queryset()
    
class CategoryViewSet(QuizCustomView):
    """Category management endpoints"""
    queryset = Category.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CategorySerializer
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def quizzes(self, request, pk=None):
        """Get all quizzes in a category"""
        category = self.get_object()
        quizzes = Quiz.objects.filter(category=category, is_active=True)
        serializer = QuizListSerializer(quizzes, many=True)
        response = success_response(
            status_code=status.HTTP_200_OK,
            message_code="get_data",
            message={"data": serializer.data}
        )
        return Response(response, status=status.HTTP_200_OK)


class QuizViewSet(QuizCustomView):
    """Quiz management endpoints"""
    queryset = Quiz.objects.filter(is_active=True)
    filterset_fields = ['category', 'difficulty']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at', 'difficulty']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return QuizDetailSerializer
        elif self.action == 'create':
            return CreateQuizSerializer
        return QuizListSerializer

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular quizzes based on attempts"""
        popular_quizzes = Quiz.objects.filter(is_active=True).annotate(
            attempt_count=Count('attempts')
        ).order_by('-attempt_count')[:10]
        
        serializer = QuizListSerializer(popular_quizzes, many=True)
        response = success_response(
            status_code=status.HTTP_200_OK,
            message_code="get_data",
            message={"data": serializer.data}
        )
        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def recommended(self, request):
        """Get recommended quizzes for user"""
        actual_user = self.get_actual_user(request)
        
        # Get user's progress to find their preferred categories
        user_attempts = QuizAttempt.objects.filter(user=actual_user)
        preferred_categories = user_attempts.values('quiz__category').annotate(
            count=Count('id')
        ).order_by('-count')[:3]
        
        category_ids = [cat['quiz__category'] for cat in preferred_categories]
        
        if category_ids:
            recommended = Quiz.objects.filter(
                category__in=category_ids, is_active=True
            ).exclude(
                id__in=user_attempts.values_list('quiz_id', flat=True)
            )[:10]
        else:
            # If no history, recommend popular quizzes
            recommended = Quiz.objects.filter(is_active=True).annotate(
                attempt_count=Count('attempts')
            ).order_by('-attempt_count')[:10]
        
        serializer = QuizListSerializer(recommended, many=True)
        response = success_response(
            status_code=status.HTTP_200_OK,
            message_code="get_data",
            message={"data": serializer.data}
        )
        return Response(response, status=status.HTTP_200_OK)


class QuizGameViewSet(QuizCustomView):
    """Quiz game play endpoints with action decorators"""
    
    def get_actual_user(self, request):
        """Get actual User instance from database to avoid TokenUser issues"""
        from account.models import User
        return User.objects.get(id=request.user.id)

    @action(detail=False, methods=['post'], url_path='start')
    def start_quiz(self, request):
        """Start a new quiz attempt"""
        serializer = StartQuizSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        quiz_id = serializer.validated_data['quiz_id']
        quiz = Quiz.objects.get(id=quiz_id)
        actual_user = self.get_actual_user(request)
        
        # Check if user has an active attempt
        active_attempt = QuizAttempt.objects.filter(
            user=actual_user, quiz=quiz, status='in_progress'
        ).first()
        
        if active_attempt:
            attempt_serializer = QuizAttemptSerializer(active_attempt)
        else:
            # Create new attempt
            attempt = QuizAttempt.objects.create(
                user=actual_user,
                quiz=quiz,
                status='in_progress'
            )
            attempt_serializer = QuizAttemptSerializer(attempt)
        
        response = success_response(
            status_code=status.HTTP_201_CREATED,
            message_code="quiz_started",
            message={
                "attempt": attempt_serializer.data,
                "quiz": QuizDetailSerializer(quiz).data
            }
        )
        return Response(response, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='submit_answer')
    def submit_answer(self, request):
        """Submit answer for a question"""
        serializer = SubmitAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        question_id = serializer.validated_data['question_id']
        answer_id = serializer.validated_data.get('answer_id')
        text_answer = serializer.validated_data.get('text_answer', '')
        
        question = Question.objects.get(id=question_id)
        actual_user = self.get_actual_user(request)
        
        # Find the active attempt
        attempt = QuizAttempt.objects.filter(
            user=actual_user, quiz=question.quiz, status='in_progress'
        ).first()
        
        if not attempt:
            return Response(
                error_response(message="No active quiz attempt found"),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already answered
        user_answer, created = UserAnswer.objects.get_or_create(
            attempt=attempt,
            question=question,
            defaults={
                'selected_answer_id': answer_id,
                'text_answer': text_answer
            }
        )
        
        if not created:
            # Update existing answer
            user_answer.selected_answer_id = answer_id
            user_answer.text_answer = text_answer
        
        # Check if answer is correct
        if question.question_type != 'fill_blank' and answer_id:
            selected_answer = Answer.objects.get(id=answer_id)
            user_answer.is_correct = selected_answer.is_correct
        
        user_answer.save()
        
        response = success_response(
            status_code=status.HTTP_200_OK,
            message_code="answer_submitted",
            message={"message": "Answer submitted successfully"}
        )
        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='finish')
    def finish_quiz(self, request):
        """Finish quiz and calculate results"""
        attempt_id = request.data.get('attempt_id')
        actual_user = self.get_actual_user(request)
        
        try:
            attempt = QuizAttempt.objects.get(
                id=attempt_id, user=actual_user, status='in_progress'
            )
        except QuizAttempt.DoesNotExist:
            return Response(
                error_response(message="Quiz attempt not found"),
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Calculate score
        total_questions = attempt.quiz.questions.filter(is_active=True).count()
        correct_answers = attempt.user_answers.filter(is_correct=True).count()
        
        if total_questions > 0:
            percentage = (correct_answers / total_questions) * 100
            score = int(percentage)
        else:
            percentage = 0
            score = 0
        
        # Update attempt
        attempt.status = 'completed'
        attempt.score = score
        attempt.percentage = percentage
        attempt.passed = percentage >= attempt.quiz.pass_score
        attempt.completed_at = timezone.now()
        attempt.time_taken = int((attempt.completed_at - attempt.started_at).total_seconds())
        attempt.save()
        
        # Update user progress
        progress, created = UserProgress.objects.get_or_create(
            user=actual_user,
            defaults={
                'total_points': 0,
                'total_quizzes_taken': 0,
                'total_quizzes_passed': 0,
                'current_streak': 0,
                'longest_streak': 0,
                'level': 1
            }
        )
        
        progress.total_quizzes_taken += 1
        if attempt.passed:
            progress.total_quizzes_passed += 1
            progress.total_points += attempt.quiz.points_reward
            
            # Update streak
            if progress.last_quiz_date == date.today():
                pass  # Same day, don't update streak
            elif progress.last_quiz_date == date.today() - timezone.timedelta(days=1):
                progress.current_streak += 1
            else:
                progress.current_streak = 1
            
            if progress.current_streak > progress.longest_streak:
                progress.longest_streak = progress.current_streak
        else:
            progress.current_streak = 0
        
        progress.last_quiz_date = date.today()
        progress.level = (progress.total_points // 100) + 1  # Level up every 100 points
        progress.save()
        
        # Check for new badges (simplified)
        new_badges = []
        if attempt.passed:
            # Check score-based badges
            score_badges = Badge.objects.filter(
                badge_type='score',
                points_required__lte=progress.total_points,
                is_active=True
            ).exclude(
                id__in=UserBadge.objects.filter(user=actual_user).values_list('badge_id', flat=True)
            )
            
            for badge in score_badges:
                UserBadge.objects.get_or_create(user=actual_user, badge=badge)
                new_badges.append(badge)
        
        # Prepare response data
        user_answers = UserAnswer.objects.filter(attempt=attempt).select_related('question', 'selected_answer')
        
        response_data = {
            "attempt": QuizAttemptSerializer(attempt).data,
            "user_answers": UserAnswerSerializer(user_answers, many=True).data,
            "badges_earned": BadgeSerializer(new_badges, many=True).data,
            "progress": UserProgressSerializer(progress).data
        }
        
        response = success_response(
            status_code=status.HTTP_200_OK,
            message_code="quiz_completed",
            message=response_data
        )
        return Response(response, status=status.HTTP_200_OK)


class UserProgressView(APIView):
    """User progress and statistics"""
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTStatelessUserAuthentication]

    def get_actual_user(self, request):
        """Get actual User instance from database to avoid TokenUser issues"""
        from account.models import User
        return User.objects.get(id=request.user.id)

    def get(self, request):
        """Get user progress"""
        actual_user = self.get_actual_user(request)
        progress, created = UserProgress.objects.get_or_create(
            user=actual_user,
            defaults={
                'total_points': 0,
                'total_quizzes_taken': 0,
                'total_quizzes_passed': 0,
                'current_streak': 0,
                'longest_streak': 0,
                'level': 1
            }
        )
        
        serializer = UserProgressSerializer(progress)
        response = success_response(
            status_code=status.HTTP_200_OK,
            message_code="get_data",
            message={"data": serializer.data}
        )
        return Response(response, status=status.HTTP_200_OK)


class LeaderboardViewSet(QuizCustomView):
    """Leaderboard endpoints using custom viewset"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = UserProgress.objects.select_related('user').order_by('-total_points')
    serializer_class = UserProgressSerializer
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        """Get leaderboard"""
        # Get top users by total points
        queryset = self.get_queryset()[:50]
        
        leaderboard_data = []
        for rank, progress in enumerate(queryset, 1):
            leaderboard_data.append({
                'rank': rank,
                'user_email': progress.user.email,
                'user_name': f"{progress.user.first_name} {progress.user.last_name}".strip() or progress.user.email,
                'points': progress.total_points,
                'level': progress.level,
                'quizzes_passed': progress.total_quizzes_passed
            })
        
        response = success_response(
            status_code=status.HTTP_200_OK,
            message_code="get_data",
            message={"data": leaderboard_data}
        )
        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get leaderboard filtered by category"""
        category_id = request.query_params.get('category_id')
        
        if not category_id:
            return Response(
                error_response(message="category_id parameter required"),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Filter users who have taken quizzes in this category
        user_ids = QuizAttempt.objects.filter(
            quiz__category_id=category_id,
            status='completed'
        ).values_list('user_id', flat=True).distinct()
        
        queryset = self.get_queryset().filter(user_id__in=user_ids)[:50]
        
        leaderboard_data = []
        for rank, progress in enumerate(queryset, 1):
            leaderboard_data.append({
                'rank': rank,
                'user_email': progress.user.email,
                'user_name': f"{progress.user.first_name} {progress.user.last_name}".strip() or progress.user.email,
                'points': progress.total_points,
                'level': progress.level,
                'quizzes_passed': progress.total_quizzes_passed
            })
        
        response = success_response(
            status_code=status.HTTP_200_OK,
            message_code="get_data",
            message={"data": leaderboard_data}
        )
        return Response(response, status=status.HTTP_200_OK)


class BadgeViewSet(QuizCustomView):
    """Badge management"""
    queryset = Badge.objects.filter(is_active=True)
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_badges(self, request):
        """Get user's earned badges"""
        actual_user = self.get_actual_user(request)
        user_badges = UserBadge.objects.filter(user=actual_user).select_related('badge')
        serializer = UserBadgeSerializer(user_badges, many=True)
        response = success_response(
            status_code=status.HTTP_200_OK,
            message_code="get_data",
            message={"data": serializer.data}
        )
        return Response(response, status=status.HTTP_200_OK)
