# CyberQuest Django Model Structure

This directory contains the complete Django model structure for the CyberQuest cybersecurity learning platform.

## Model Organization

### 1. User Models (`user_models.py`)
- **User**: Extended Django user model with cybersecurity-specific fields
- **Category**: Cybersecurity topic categories (Phishing, OSINT, Network Security, etc.)
- **Tag**: Flexible tagging system for content organization
- **Question**: Core quiz questions with multiple types and difficulties
- **QuestionOption**: Answer choices for multiple-choice questions
- **Quiz**: Collections of questions forming quizzes and challenges
- **QuizQuestion**: Junction table for quiz-question relationships
- **UserAttempt**: Individual question attempts by users
- **QuizSession**: Track complete quiz sessions

### 2. Gamification Models (`gamification_models.py`)
- **Badge**: Achievement badges with different types and rarities
- **UserBadge**: User-earned badges with timestamps
- **Leaderboard**: Different leaderboard types (global, category, weekly, etc.)
- **LeaderboardEntry**: Individual leaderboard positions
- **UserProgress**: Category-specific progress tracking
- **UserStreak**: Daily activity streaks
- **Notification**: User notification system
- **UserPreference**: User settings and preferences

### 3. Content Models (`content_models.py`)
- **Challenge**: Special timed challenges and events
- **ChallengeParticipation**: User participation in challenges
- **LearningPath**: Structured learning sequences
- **LearningPathStep**: Individual steps in learning paths
- **UserLearningProgress**: Progress through learning paths
- **UserStepProgress**: Completion of individual steps
- **Report**: Content reporting system

### 4. Admin Models (`admin_models.py`)
- **AuditLog**: System event logging with generic foreign keys
- **SystemConfiguration**: Dynamic system settings
- **Feedback**: User feedback and bug reports
- **Announcement**: System announcements and news
- **UserAnnouncementRead**: Track read announcements
- **Analytics**: Analytics data storage

## Key Features

### User Management
- Role-based access (student, instructor, admin)
- Skill level progression
- Social features (GitHub, LinkedIn integration)
- Privacy controls and preferences

### Question System
- Multiple question types (multiple choice, true/false, code analysis, etc.)
- Difficulty levels and category organization
- Rich content support (images, code snippets)
- Comprehensive explanation system

### Gamification
- Badge system with multiple achievement types
- Streak tracking and rewards
- Multiple leaderboard types
- Progress tracking per category

### Learning Paths
- Structured learning sequences
- Prerequisites and dependencies
- Progress tracking
- Mixed content types (quizzes, reading, videos)

### Admin Features
- Comprehensive audit logging
- System configuration management
- User feedback system
- Analytics data collection

## Database Considerations

### Indexes
- Strategic indexes on frequently queried fields
- Composite indexes for complex queries
- Foreign key indexes for join performance

### Relationships
- Proper use of ForeignKey, ManyToMany, and OneToOne
- Generic foreign keys for flexible content relationships
- Cascade behaviors for data integrity

### Validation
- Built-in Django validators
- Custom validation methods
- Constraint validation at database level

## Setup Instructions

1. Install dependencies: `pip install -r requirements.txt`
2. Configure database settings in `settings.py`
3. Run migrations: `python manage.py makemigrations && python manage.py migrate`
4. Create superuser: `python manage.py createsuperuser`
5. Load initial data: `python manage.py loaddata fixtures/*.json`

## API Integration

Models are designed to work seamlessly with Django REST Framework:
- Comprehensive serializers for all models
- ViewSets with filtering, searching, and pagination
- Authentication and permission integration
- API documentation with drf-yasg

## Security Features

- User authentication and authorization
- Content reporting system
- Audit logging for security monitoring
- IP address tracking for suspicious activity
- Secure file upload handling

This model structure provides a solid foundation for a comprehensive cybersecurity learning platform with modern features and scalability considerations.
