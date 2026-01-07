from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil
from PIL import Image


class Command(BaseCommand):
    help = 'Copia arquivos PNG de fotos_para_app para static/pwa-icons'

    def handle(self, *args, **options):
        src_dir = os.path.join(settings.BASE_DIR, 'fotos_para_app')
        dest_dir = os.path.join(settings.BASE_DIR, 'static', 'img')
        if not os.path.exists(src_dir):
            self.stderr.write(f'Fonte não encontrada: {src_dir}')
            return
        os.makedirs(dest_dir, exist_ok=True)
        count = 0
        for fname in os.listdir(src_dir):
            if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
                src = os.path.join(src_dir, fname)
                dest = os.path.join(dest_dir, fname)
                try:
                    shutil.copy2(src, dest)
                    count += 1
                except Exception as e:
                    self.stderr.write(f'Erro copiando {fname}: {e}')
        self.stdout.write(self.style.SUCCESS(f'Copiados {count} arquivos para {dest_dir}'))
        # Gerar um PNG `logo.png` a partir do melhor candidato copiado (prefere 512, senão o maior disponível)
        try:
            candidates = [f for f in os.listdir(dest_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            best = None
            if candidates:
                # preferir nome com 512 se existir
                for c in candidates:
                    if '512' in c:
                        best = c
                        break
                if not best:
                    # escolher o arquivo com maior número em seu nome, se houver
                    def numeric_key(name):
                        import re
                        nums = re.findall(r"(\d+)", name)
                        return int(nums[-1]) if nums else 0
                    best = max(candidates, key=numeric_key)

                src_logo = os.path.join(dest_dir, best)
                out_logo = os.path.join(dest_dir, 'logo.png')
                try:
                    with Image.open(src_logo) as im:
                        im.convert('RGBA').save(out_logo, format='PNG')
                    self.stdout.write(self.style.SUCCESS(f'Criado logo PNG: {out_logo} (origem: {best})'))
                except Exception as e:
                    self.stderr.write(f'Falha criando logo.png a partir de {best}: {e}')
        except Exception:
            pass
        # Remover a imagem antiga se existir
        old = os.path.join(dest_dir, 'web_hi_res_512-Photoroom.png')
        if os.path.exists(old):
            try:
                os.remove(old)
                self.stdout.write(self.style.SUCCESS(f'Removido arquivo antigo: {old}'))
            except Exception as e:
                self.stderr.write(f'Falha ao remover {old}: {e}')
