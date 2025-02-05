from django.apps import AppConfig

class LoggerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'logger'

    def ready(self):
        import logger.signals  # シグナルを登録
