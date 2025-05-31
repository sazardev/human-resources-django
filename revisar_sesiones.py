#!/usr/bin/env python
"""
Script para revisar y gestionar las sesiones de usuario
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from authentication.models import User, UserSession, LoginAttempt
from django.utils import timezone

def revisar_sesiones():
    """Revisar todas las sesiones de usuario"""
    print("🔍 REVISIÓN DE SESIONES DE USUARIO")
    print("=" * 50)
    
    # Obtener todas las sesiones
    sesiones = UserSession.objects.all().order_by('-created_at')
    
    print(f"Total de sesiones: {sesiones.count()}")
    print()
    
    for sesion in sesiones:
        estado = "🟢 ACTIVA" if sesion.is_active else "🔴 INACTIVA"
        duracion = sesion.last_activity - sesion.created_at
        
        print(f"Usuario: {sesion.user.email}")
        print(f"Estado: {estado}")
        print(f"IP: {sesion.ip_address}")
        print(f"Creada: {sesion.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"Última actividad: {sesion.last_activity.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"Duración: {duracion}")
        print(f"Session Key: {sesion.session_key}")
        print("-" * 30)

def revisar_intentos_login():
    """Revisar intentos de login"""
    print("\n🔐 REVISIÓN DE INTENTOS DE LOGIN")
    print("=" * 50)
    
    intentos = LoginAttempt.objects.all().order_by('-attempted_at')[:10]
    
    for intento in intentos:
        estado = "✅ EXITOSO" if intento.success else "❌ FALLIDO"
        print(f"Email: {intento.email}")
        print(f"Estado: {estado}")
        print(f"IP: {intento.ip_address}")
        print(f"Fecha: {intento.attempted_at.strftime('%d/%m/%Y %H:%M:%S')}")
        if intento.failure_reason:
            print(f"Razón: {intento.failure_reason}")
        print("-" * 30)

def marcar_sesiones_inactivas():
    """Marcar sesiones antiguas como inactivas"""
    print("\n🔧 MARCANDO SESIONES ANTIGUAS COMO INACTIVAS")
    print("=" * 50)
    
    # Marcar como inactivas las sesiones de más de 24 horas sin actividad
    tiempo_limite = timezone.now() - timedelta(hours=24)
    
    sesiones_antiguas = UserSession.objects.filter(
        last_activity__lt=tiempo_limite,
        is_active=True
    )
    
    count = sesiones_antiguas.count()
    sesiones_antiguas.update(is_active=False)
    
    print(f"Se marcaron {count} sesiones como inactivas")

def estadisticas_sesiones():
    """Mostrar estadísticas de sesiones"""
    print("\n📊 ESTADÍSTICAS DE SESIONES")
    print("=" * 50)
    
    total_sesiones = UserSession.objects.count()
    sesiones_activas = UserSession.objects.filter(is_active=True).count()
    sesiones_inactivas = UserSession.objects.filter(is_active=False).count()
    
    # Sesiones por usuario
    usuarios_con_sesiones = User.objects.filter(user_sessions__isnull=False).distinct().count()
    
    # Intentos de login
    total_intentos = LoginAttempt.objects.count()
    intentos_exitosos = LoginAttempt.objects.filter(success=True).count()
    intentos_fallidos = LoginAttempt.objects.filter(success=False).count()
    
    print(f"📈 Sesiones:")
    print(f"   Total: {total_sesiones}")
    print(f"   Activas: {sesiones_activas}")
    print(f"   Inactivas: {sesiones_inactivas}")
    print(f"   Usuarios con sesiones: {usuarios_con_sesiones}")
    print()
    print(f"🔐 Intentos de Login:")
    print(f"   Total: {total_intentos}")
    print(f"   Exitosos: {intentos_exitosos}")
    print(f"   Fallidos: {intentos_fallidos}")
    if total_intentos > 0:
        tasa_exito = (intentos_exitosos / total_intentos) * 100
        print(f"   Tasa de éxito: {tasa_exito:.1f}%")

if __name__ == "__main__":
    print("🚀 SISTEMA DE GESTIÓN DE SESIONES")
    print("=" * 50)
    
    # Ejecutar todas las funciones
    revisar_sesiones()
    revisar_intentos_login()
    marcar_sesiones_inactivas()
    estadisticas_sesiones()
    
    print("\n✅ Revisión completada!")
