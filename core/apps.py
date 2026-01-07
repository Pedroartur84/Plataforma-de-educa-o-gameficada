from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Tenta copiar ícones para static/pwa-icons automaticamente no startup
        try:
            from django.core.management import call_command
            call_command('copy_pwa_icons')
        except Exception:
            # Não falhar o startup por causa da cópia de ícones
            pass
