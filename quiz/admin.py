from django.contrib import admin
from .models import (
    Category, Quiz, Question, Answer, QuizAttempt,
    Badge, UserProgress, Leaderboard
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty', 'total_questions', 'is_active', 'created_at']
    list_filter = ['category', 'difficulty', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'question_text', 'question_type', 'points', 'order', 'is_active']
    list_filter = ['question_type', 'quiz__category', 'is_active']
    search_fields = ['question_text', 'quiz__title']
    inlines = [AnswerInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'status', 'score', 'percentage', 'passed', 'started_at']
    list_filter = ['status', 'passed', 'quiz__category', 'started_at']
    search_fields = ['user__email', 'quiz__title']
    readonly_fields = ['started_at', 'completed_at']


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'badge_type', 'points_required', 'category', 'is_active']
    list_filter = ['badge_type', 'category', 'is_active']
    search_fields = ['name', 'description']


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'level', 'total_points', 'total_quizzes_taken', 'current_streak']
    list_filter = ['level', 'last_quiz_date']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ['user', 'period', 'category', 'points', 'rank', 'period_start']
    list_filter = ['period', 'category', 'period_start']
    search_fields = ['user__email']
