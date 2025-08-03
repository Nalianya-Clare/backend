# Quiz App - API Endpoints & Model Structure

## Overview
Complete Django app with REST API endpoints for quiz functionality using the User model from the `account` app.

## API Endpoints

### **Categories**
```
GET    /quiz/categories/              - List all categories
POST   /quiz/categories/              - Create new category
GET    /quiz/categories/{id}/         - Get category details
PUT    /quiz/categories/{id}/         - Update category
DELETE /quiz/categories/{id}/         - Delete category
GET    /quiz/categories/{id}/quizzes/ - Get quizzes in category
```

### **Quizzes**
```
GET    /quiz/quizzes/                 - List all quizzes (with filtering)
POST   /quiz/quizzes/                 - Create new quiz
GET    /quiz/quizzes/{id}/            - Get quiz details with questions
PUT    /quiz/quizzes/{id}/            - Update quiz
DELETE /quiz/quizzes/{id}/            - Delete quiz
GET    /quiz/quizzes/popular/         - Get popular quizzes
GET    /quiz/quizzes/recommended/     - Get recommended quizzes for user
```

### **Quiz Game**
```
POST   /quiz/game/start               - Start a quiz attempt
POST   /quiz/game/submit_answer       - Submit answer to question
POST   /quiz/game/finish              - Finish quiz and get results
```

### **User Progress**
```
GET    /quiz/progress                 - Get user's progress and statistics
```

### **Leaderboard**
```
GET    /quiz/leaderboard              - Get leaderboard rankings
```

### **Badges**
```
GET    /quiz/badges/                  - List all available badges
GET    /quiz/badges/my_badges/        - Get user's earned badges
```

## Request/Response Examples

### **Start Quiz**
```json
POST /quiz/game/start
{
  "quiz_id": 1
}

Response:
{
  "status_code": 201,
  "message_code": "quiz_started",
  "message": {
    "attempt": {
      "id": 1,
      "quiz": 1,
      "status": "in_progress",
      "started_at": "2025-08-03T10:00:00Z"
    },
    "quiz": {
      "id": 1,
      "title": "Python Basics",
      "questions": [...]
    }
  }
}
```

### **Submit Answer**
```json
POST /quiz/game/submit_answer
{
  "question_id": 1,
  "answer_id": 3
}

Response:
{
  "status_code": 200,
  "message_code": "answer_submitted",
  "message": {
    "message": "Answer submitted successfully"
  }
}
```

### **Finish Quiz**
```json
POST /quiz/game/finish
{
  "attempt_id": 1
}

Response:
{
  "status_code": 200,
  "message_code": "quiz_completed",
  "message": {
    "attempt": {
      "score": 85,
      "percentage": 85.0,
      "passed": true,
      "time_taken": 180
    },
    "user_answers": [...],
    "badges_earned": [...],
    "progress": {
      "level": 2,
      "total_points": 150,
      "current_streak": 3
    }
  }
}
```

## Model Hierarchy & Relationships

```
User (from account.models)
├── Created Quizzes (Quiz.created_by)
├── Quiz Attempts (QuizAttempt.user)
├── Progress Tracking (UserProgress.user - OneToOne)
├── Earned Badges (UserBadge.user)
└── Leaderboard Entries (Leaderboard.user)

Category
├── Quizzes (Quiz.category)
└── Badges (Badge.category)

Quiz
├── Questions (Question.quiz)
├── Attempts (QuizAttempt.quiz)
└── Created by User (Quiz.created_by)

Question
├── Answers (Answer.question)
└── User Answers (UserAnswer.question)

QuizAttempt
└── User Answers (UserAnswer.attempt)
```

## Core Models

### 1. **Category**
- Organizes quizzes by topic/subject
- Simple categorization with icon and color

### 2. **Quiz**
- Main quiz entity
- Contains metadata: title, description, difficulty, time limit
- Links to Category and created by User

### 3. **Question**
- Individual quiz questions
- Supports multiple choice, true/false, fill-in-blank
- Ordered within quiz

### 4. **Answer**
- Answer choices for questions
- Marks correct answers

### 5. **QuizAttempt**
- Tracks user quiz sessions
- Records score, time, completion status

### 6. **UserAnswer**
- Individual question responses
- Links attempt to specific answers

### 7. **UserProgress**
- Tracks overall user statistics
- Points, streaks, level progression

### 8. **Badge & UserBadge**
- Achievement system
- Earned badges tracked per user

## Features Implemented

### **Complete REST API**
- Following account app patterns
- Custom views with proper authentication
- Standardized response format
- Pagination and filtering

### **Quiz Flow**
1. User browses categories/quizzes
2. Starts quiz attempt
3. Submits answers question by question
4. Finishes quiz with results
5. Progress and badges updated automatically

### **Gamification**
- Points and leveling system
- Achievement badges
- Streak tracking
- Leaderboards

### **Advanced Features**
- Quiz recommendations based on user history
- Popular quizzes tracking
- Time tracking for attempts
- Progress analytics

## Query Parameters

### **Quiz List**
```
GET /quiz/quizzes/?category=1&difficulty=easy&search=python&ordering=-created_at
```

### **Leaderboard**
```
GET /quiz/leaderboard/?period=weekly&category=1
```

## Authentication
All endpoints require JWT authentication using the account app's User model.

## File Structure
```
quiz/
├── models.py          # 9 models with relationships
├── serializers.py     # 15+ serializers for API
├── views.py           # 6 viewsets/views with endpoints
├── admin.py           # Complete admin interface
├── urls.py            # All endpoint routes
├── apps.py            # App configuration
└── README.md          # This documentation
```

## Installation Steps
1. Add `'quiz'` to `INSTALLED_APPS` in settings
2. Run `python manage.py makemigrations quiz`
3. Run `python manage.py migrate`
4. Add quiz URLs to main urls.py:
   ```python
   path('quiz/', include('quiz.urls')),
   ```
5. Start using the API endpoints!

## Usage Examples

### **Create Quiz with Questions**
```json
POST /quiz/quizzes/
{
  "title": "Python Basics",
  "description": "Test your Python knowledge",
  "category": 1,
  "difficulty": "easy",
  "time_limit": 30,
  "total_questions": 5,
  "questions_data": [
    {
      "question_text": "What is Python?",
      "question_type": "multiple_choice",
      "order": 1,
      "answers": [
        {"answer_text": "A snake", "is_correct": false, "order": 1},
        {"answer_text": "A programming language", "is_correct": true, "order": 2}
      ]
    }
  ]
}
```

This implementation provides a complete, production-ready quiz system with all endpoints exposed following your account app patterns!
