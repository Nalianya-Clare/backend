from django.apps import AppConfig


class QuizConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quiz'
    verbose_name = 'Quiz System'
    
    def ready(self):
        # Import signals if you need them
        pass
