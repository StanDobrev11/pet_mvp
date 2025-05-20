from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pet_mvp.accounts'

    def ready(self):
        import pet_mvp.accounts.signals