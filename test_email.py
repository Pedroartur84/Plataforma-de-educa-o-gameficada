#!/usr/bin/env python
"""
Script para testar envio de email via SendGrid API
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
import logging

logging.basicConfig(level=logging.DEBUG)

print("=" * 70)
print("TESTE DE ENVIO DE EMAIL - SendGrid API Backend")
print("=" * 70)
print(f"Backend configurado: {settings.EMAIL_BACKEND}")
print(f"Remetente: {settings.DEFAULT_FROM_EMAIL}")
print(f"API Key definida: {bool(settings.SENDGRID_API_KEY)}")
print(f"DEBUG mode: {settings.DEBUG}")
print("=" * 70)

# ⚠️ IMPORTANTE: Troque 'seu_email_teste@example.com' por um email real seu
email_teste = 'pedroarturfelixdemelo@gmail.com'

if email_teste == 'seu_email_teste@example.com':
    print("\n⚠️  ATENÇÃO: Você precisa trocar 'seu_email_teste@example.com' por um email real!")
    print("   Edite este arquivo (test_email.py) e coloque um email válido na linha 27.")
    sys.exit(1)

print(f"\nEnviando email de teste para: {email_teste}\n")

try:
    result = send_mail(
        subject='Teste SendGrid API - Django',
        message='Este é um teste do backend de API do SendGrid no Render free tier.\n\nSe você recebeu este email, significa que a configuração está funcionando!',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email_teste],
        fail_silently=False,
    )
    print(f"\n✅ EMAIL ENVIADO COM SUCESSO!")
    print(f"   Quantidade de emails enviados: {result}")
    print(f"\n   Verifique sua caixa de entrada em {email_teste}")
    print(f"   (Pode levar alguns segundos para chegar)")
    
except Exception as e:
    print(f"\n❌ ERRO AO ENVIAR EMAIL")
    print(f"   Tipo de erro: {type(e).__name__}")
    print(f"   Mensagem: {str(e)}")
    print("\n" + "=" * 70)
    print("DIAGNÓSTICO:")
    print("=" * 70)
    
    error_msg = str(e).lower()
    
    if '401' in error_msg or 'unauthorized' in error_msg:
        print("❌ Erro 401 - Unauthorized")
        print("   CAUSA: API Key inválida ou expirada")
        print("   SOLUÇÃO:")
        print("   1. Verifique se SENDGRID_API_KEY está definida no Render")
        print("   2. Gere uma nova API Key no SendGrid (Settings > API Keys)")
        print("   3. Atualize a variável no Render com a nova chave")
    
    elif '403' in error_msg or 'forbidden' in error_msg:
        print("❌ Erro 403 - Forbidden")
        print("   CAUSA: Sender não verificado ou sem permissão")
        print("   SOLUÇÃO:")
        print("   1. Vá para SendGrid > Settings > Sender Authentication")
        print("   2. Verifique se 'contatoplayer040@gmail.com' tem status VERIFIED")
        print("   3. Se não, clique em 'Resend Verification Email'")
        print("   4. Confirme o email no inbox do Gmail")
    
    elif 'timeout' in error_msg or 'connection' in error_msg:
        print("❌ Erro de Conexão/Timeout")
        print("   CAUSA: Problema de conectividade com API do SendGrid")
        print("   SOLUÇÃO:")
        print("   1. Verifique internet (deve estar OK)")
        print("   2. Aguarde alguns segundos e tente novamente")
        print("   3. Se persistir, pode ser bloqueio temporário de IP")
    
    else:
        print(f"❌ Erro desconhecido: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
    
    print("\n" + "=" * 70)
    import traceback
    print("TRACEBACK COMPLETO:")
    print("=" * 70)
    traceback.print_exc()

print("\n" + "=" * 70)
