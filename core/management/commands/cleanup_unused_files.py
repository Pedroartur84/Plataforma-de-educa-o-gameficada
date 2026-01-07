from django.core.management.base import BaseCommand
from django.conf import settings
import shutil
import os


class Command(BaseCommand):
    help = 'Remove diretórios desnecessários: fotos_para_app e static/pwa-icons'

    def handle(self, *args, **options):
        base = settings.BASE_DIR
        targets = [
            os.path.join(base, 'fotos_para_app'),
            os.path.join(base, 'static', 'pwa-icons'),
        ]
        for t in targets:
            if os.path.exists(t):
                try:
                    shutil.rmtree(t)
                    self.stdout.write(self.style.SUCCESS(f'Removido: {t}'))
                except Exception as e:
                    self.stderr.write(f'Falha removendo {t}: {e}')
            else:
                self.stdout.write(self.style.NOTICE(f'Não encontrado (ignorado): {t}'))
