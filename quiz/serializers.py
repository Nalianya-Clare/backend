from rest_framework import serializers
from .models import (
    Category, Quiz, Question, Answer, QuizAttempt, UserAnswer,
    Badge, UserBadge, UserProgress, Leaderboard, Resource
)


class CategorySerializer(serializers.ModelSerializer):
    quiz_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'color', 'is_active', 'created_at', 'quiz_count']
        read_only_fields = ['created_at']
    
    def get_quiz_count(self, obj):
        return obj.quizzes.filter(is_active=True).count()


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'answer_text', 'is_correct', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'explanation', 'points', 'order', 'answers']


class QuizListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.first_name', read_only=True)
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'category', 'category_name', 'difficulty', 
                 'time_limit', 'total_questions', 'pass_score', 'points_reward', 'start_time',
                 'created_by_name', 'created_at', 'question_count']
        read_only_fields = ['created_at']
    
    def get_question_count(self, obj):
        return obj.questions.filter(is_active=True).count()


class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'category', 'category_name', 'difficulty',
                 'time_limit', 'total_questions', 'pass_score', 'points_reward',
                 'questions', 'created_at']
        read_only_fields = ['created_at']


class StartQuizSerializer(serializers.Serializer):
    quiz_id = serializers.IntegerField()
    
    def validate_quiz_id(self, value):
        try:
            Quiz.objects.get(id=value, is_active=True)
            return value
        except Quiz.DoesNotExist:
            raise serializers.ValidationError("Quiz not found or inactive")


class SubmitAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer_id = serializers.IntegerField(required=False, allow_null=True)
    text_answer = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        question_id = data.get('question_id')
        answer_id = data.get('answer_id')
        text_answer = data.get('text_answer')
        
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            raise serializers.ValidationError("Question not found")
        
        if question.question_type == 'fill_blank':
            if not text_answer:
                raise serializers.ValidationError("Text answer required for fill-in-the-blank questions")
        else:
            if not answer_id:
                raise serializers.ValidationError("Answer selection required")
            try:
                Answer.objects.get(id=answer_id, question=question)
            except Answer.DoesNotExist:
                raise serializers.ValidationError("Invalid answer for this question")
        
        return data


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'quiz_title', 'user_email', 'status', 'score', 
                 'percentage', 'time_taken', 'passed', 'started_at', 'completed_at']
        read_only_fields = ['user', 'started_at', 'completed_at']


class UserAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    selected_answer_text = serializers.CharField(source='selected_answer.answer_text', read_only=True)
    correct_answer = serializers.SerializerMethodField()
    
    class Meta:
        model = UserAnswer
        fields = ['id', 'question', 'question_text', 'selected_answer', 'selected_answer_text',
                 'text_answer', 'is_correct', 'correct_answer', 'answered_at']
    
    def get_correct_answer(self, obj):
        if obj.question.question_type == 'fill_blank':
            return "Check explanation for correct answer"
        correct_answer = obj.question.answers.filter(is_correct=True).first()
        return correct_answer.answer_text if correct_answer else None


class BadgeSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Badge
        fields = ['id', 'name', 'description', 'badge_type', 'icon', 'color',
                 'points_required', 'category', 'category_name', 'is_active']


class UserBadgeSerializer(serializers.ModelSerializer):
    badge_details = BadgeSerializer(source='badge', read_only=True)
    
    class Meta:
        model = UserBadge
        fields = ['id', 'badge', 'badge_details', 'earned_at']


class UserProgressSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    badges_earned = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProgress
        fields = ['id', 'user_email', 'total_points', 'total_quizzes_taken', 
                 'total_quizzes_passed', 'current_streak', 'longest_streak',
                 'last_quiz_date', 'level', 'badges_earned', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def get_badges_earned(self, obj):
        return obj.user.badges.count()


class LeaderboardSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Leaderboard
        fields = ['id', 'user_email', 'user_name', 'period', 'category', 'category_name',
                 'points', 'rank', 'period_start', 'period_end']
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email


class QuizResultSerializer(serializers.Serializer):
    attempt = QuizAttemptSerializer()
    user_answers = UserAnswerSerializer(many=True)
    badges_earned = BadgeSerializer(many=True)
    progress = UserProgressSerializer()


class CreateQuizSerializer(serializers.ModelSerializer):
    questions_data = serializers.ListField(write_only=True, required=False)
    
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'category', 'difficulty', 'time_limit',
                 'total_questions', 'pass_score', 'start_time', 'points_reward', 'questions_data']

    def create(self, validated_data):
        from account.models import User
        
        questions_data = validated_data.pop('questions_data', [])
        
        # Get the actual User instance from the database
        user_id = self.context['request'].user.id
        actual_user = User.objects.get(id=user_id)
        validated_data['created_by'] = actual_user
        
        quiz = Quiz.objects.create(**validated_data)
        
        for question_data in questions_data:
            answers_data = question_data.pop('answers', [])
            question = Question.objects.create(quiz=quiz, **question_data)
            
            for answer_data in answers_data:
                Answer.objects.create(question=question, **answer_data)
        
        return quiz


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'
