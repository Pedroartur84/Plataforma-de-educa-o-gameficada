from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil
import sys

try:
    from PIL import Image
    HAS_PIL = True
except Exception:
    HAS_PIL = False


REQUIRED = [
    'icon-192x192.jpg',
    'icon-512x512.jpg',
]


class Command(BaseCommand):
    help = 'Valida e copia ícones PWA para static/pwa-icons (procura em fotos_para_app).'

    def handle(self, *args, **options):
        base = settings.BASE_DIR
        dest = os.path.join(base, 'static', 'pwa-icons')
        src = os.path.join(base, 'fotos_para_app')

        if not os.path.isdir(dest):
            os.makedirs(dest, exist_ok=True)
            self.stdout.write(self.style.SUCCESS(f'Criado diretório {dest}'))

        missing = []
        for name in REQUIRED:
            dest_path = os.path.join(dest, name)
            if not os.path.exists(dest_path):
                src_path = os.path.join(src, name)
                if os.path.exists(src_path):
                    shutil.copy2(src_path, dest_path)
                    self.stdout.write(self.style.SUCCESS(f'Copiado {name} -> static/pwa-icons'))
                else:
                    missing.append(name)

        # listar todos os arquivos no dest
        all_files = [f for f in os.listdir(dest) if os.path.isfile(os.path.join(dest, f))]
        self.stdout.write('Arquivos em static/pwa-icons:')
        for f in all_files:
            line = f'- {f}'
            if HAS_PIL:
                try:
                    p = os.path.join(dest, f)
                    with Image.open(p) as im:
                        line += f' ({im.format}, {im.size[0]}x{im.size[1]})'
                except Exception:
                    pass
            self.stdout.write(line)

        if missing:
            self.stdout.write(self.style.WARNING('Arquivos obrigatórios faltando:'))
            for m in missing:
                self.stdout.write(self.style.WARNING(f' - {m}'))
            self.stdout.write('Coloque os JPEGs em fotos_para_app/ com os nomes corretos ou converta-os antes de prosseguir.')
            if not HAS_PIL:
                self.stdout.write('Recomendado instalar Pillow para validação de dimensões: pip install Pillow')
            sys.exit(2)
        else:
            self.stdout.write(self.style.SUCCESS('Validação concluída: todos os arquivos obrigatórios presentes.'))
