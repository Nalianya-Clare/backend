from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, QuizViewSet, LeaderboardViewSet, BadgeViewSet,
    UserProgressView, QuizGameViewSet
)

app_name = 'quiz'

# Setup router for viewsets
router = DefaultRouter(trailing_slash=False)
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'quizzes', QuizViewSet, basename='quizzes')
router.register(r'leaderboard', LeaderboardViewSet, basename='leaderboard')
router.register(r'badges', BadgeViewSet, basename='badges')
router.register(r'game', QuizGameViewSet, basename='game')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # User progress
    path('progress/', UserProgressView.as_view(), name='user-progress'),
]

# Available endpoints:
# GET /quiz/categories/ - List all categories
# POST /quiz/categories/ - Create category
# GET /quiz/categories/{id}/ - Get category details
# GET /quiz/categories/{id}/quizzes/ - Get quizzes in category
# 
# GET /quiz/quizzes/ - List all quizzes
# POST /quiz/quizzes/ - Create quiz
# GET /quiz/quizzes/{id}/ - Get quiz details
# GET /quiz/quizzes/popular/ - Get popular quizzes
# GET /quiz/quizzes/recommended/ - Get recommended quizzes for user
#
# POST /quiz/game/start/ - Start quiz attempt
# POST /quiz/game/submit_answer/ - Submit answer
# POST /quiz/game/finish/ - Finish quiz and get results
#
# GET /quiz/progress/ - Get user progress
#
# GET /quiz/leaderboard/ - Get leaderboard rankings
# GET /quiz/leaderboard/by_category/ - Get leaderboard by category
#
# GET /quiz/badges/ - List all badges
# GET /quiz/badges/my_badges/ - Get user's earned badges
