from django.apps import AppConfig


class PetsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pet_mvp.pets'

    def ready(self):
        import pet_mvp.pets.signals
        import pet_mvp.pets.translation
