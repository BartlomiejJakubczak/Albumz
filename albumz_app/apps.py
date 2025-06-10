from django.apps import AppConfig


class AlbumzAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'albumz_app'

    def ready(self):
        import albumz_app.signals