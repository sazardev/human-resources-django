#!/usr/bin/env python
"""
Script para probar los endpoints de autenticación del sistema HR
"""
import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://127.0.0.1:8000/api/auth"
HEADERS = {"Content-Type": "application/json"}

def print_separator(title):
    print(f"\n{'='*60}")
    print(f"🔐 {title}")
    print('='*60)

def print_response(title, response):
    print(f"\n📋 {title}")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")

def test_user_registration():
    """Probar registro de usuario"""
    print_separator("TEST: REGISTRO DE USUARIO")
    
    user_data = {
        "username": "testuser",
        "email": "test@company.com",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567890",
        "password": "test123456",
        "password_confirm": "test123456"
    }
    
    response = requests.post(f"{BASE_URL}/register/", 
                           json=user_data, 
                           headers=HEADERS)
    print_response("Registro de Usuario", response)
    
    if response.status_code == 201:
        data = response.json()
        return data.get('token')
    return None

def test_user_login():
    """Probar login de usuario"""
    print_separator("TEST: LOGIN DE USUARIO")
    
    login_data = {
        "email": "test@company.com",
        "password": "test123456",
        "remember_me": True
    }
    
    response = requests.post(f"{BASE_URL}/login/", 
                           json=login_data, 
                           headers=HEADERS)
    print_response("Login de Usuario", response)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('token')
    return None

def test_profile_access(token):
    """Probar acceso al perfil"""
    print_separator("TEST: ACCESO AL PERFIL")
    
    headers = {**HEADERS, "Authorization": f"Token {token}"}
    
    response = requests.get(f"{BASE_URL}/profile/", headers=headers)
    print_response("Obtener Perfil", response)

def test_profile_update(token):
    """Probar actualización del perfil"""
    print_separator("TEST: ACTUALIZACIÓN DEL PERFIL")
    
    headers = {**HEADERS, "Authorization": f"Token {token}"}
    
    update_data = {
        "first_name": "Test Updated",
        "last_name": "User Updated",
        "phone": "+1987654321",
        "bio": "Perfil actualizado para pruebas"
    }
    
    response = requests.put(f"{BASE_URL}/profile/", 
                          json=update_data, 
                          headers=headers)
    print_response("Actualizar Perfil", response)

def test_change_password(token):
    """Probar cambio de contraseña"""
    print_separator("TEST: CAMBIO DE CONTRASEÑA")
    
    headers = {**HEADERS, "Authorization": f"Token {token}"}
    
    password_data = {
        "current_password": "test123456",
        "new_password": "newpassword123",
        "new_password_confirm": "newpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/change-password/", 
                           json=password_data, 
                           headers=headers)
    print_response("Cambiar Contraseña", response)

def test_user_sessions(token):
    """Probar obtener sesiones del usuario"""
    print_separator("TEST: SESIONES DEL USUARIO")
    
    headers = {**HEADERS, "Authorization": f"Token {token}"}
    
    response = requests.get(f"{BASE_URL}/sessions/", headers=headers)
    print_response("Sesiones del Usuario", response)

def test_security_info(token):
    """Probar información de seguridad"""
    print_separator("TEST: INFORMACIÓN DE SEGURIDAD")
    
    headers = {**HEADERS, "Authorization": f"Token {token}"}
    
    response = requests.get(f"{BASE_URL}/security-info/", headers=headers)
    print_response("Información de Seguridad", response)

def test_logout(token):
    """Probar logout"""
    print_separator("TEST: LOGOUT")
    
    headers = {**HEADERS, "Authorization": f"Token {token}"}
    
    response = requests.post(f"{BASE_URL}/logout/", headers=headers)
    print_response("Logout", response)

def test_password_reset():
    """Probar solicitud de reset de contraseña"""
    print_separator("TEST: SOLICITUD DE RESET DE CONTRASEÑA")
    
    reset_data = {
        "email": "test@company.com"
    }
    
    response = requests.post(f"{BASE_URL}/password-reset/", 
                           json=reset_data, 
                           headers=HEADERS)
    print_response("Solicitud de Reset", response)

def run_authentication_tests():
    """Ejecutar todos los tests de autenticación"""
    print("🚀 INICIANDO TESTS DEL SISTEMA DE AUTENTICACIÓN")
    print(f"Base URL: {BASE_URL}")
    print(f"Timestamp: {datetime.now()}")
    
    # 1. Registro de usuario
    token = test_user_registration()
    
    if not token:
        # Si el registro falla, intentar login
        token = test_user_login()
    
    if token:
        print(f"\n✅ Token obtenido: {token[:20]}...")
        
        # 2. Tests que requieren autenticación
        test_profile_access(token)
        test_profile_update(token)
        test_user_sessions(token)
        test_security_info(token)
        test_change_password(token)
        
        # 3. Logout (esto invalidará el token)
        test_logout(token)
    else:
        print("\n❌ No se pudo obtener token de autenticación")
    
    # 4. Test de reset de contraseña (no requiere auth)
    test_password_reset()
    
    print_separator("RESUMEN DE TESTS COMPLETADOS")
    print("✅ Tests de autenticación completados")
    print("📋 Revisar los resultados arriba para verificar funcionalidad")

if __name__ == "__main__":
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        print("✅ Servidor Django está corriendo")
    except requests.RequestException:
        print("❌ Servidor Django no está corriendo. Ejecute:")
        print("   python manage.py runserver")
        exit(1)
    
    run_authentication_tests()
