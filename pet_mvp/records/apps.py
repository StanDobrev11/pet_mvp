from django.apps import AppConfig


class RecordsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pet_mvp.records'

    def ready(self):
        import pet_mvp.records.signals
