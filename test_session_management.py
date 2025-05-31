#!/usr/bin/env python
"""
Script completo para probar la gestión de sesiones
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/auth"

class SessionTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.user_id = None
    
    def setup_admin_token(self):
        """Obtener token de administrador"""
        print("🔐 Obteniendo token de administrador...")
        
        # Login como admin
        data = {
            "email": "admin@admin.com",
            "password": "admin"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/login/", json=data)
            if response.status_code == 200:
                result = response.json()
                self.admin_token = result.get('token')
                print(f"   ✅ Token de admin obtenido: {self.admin_token[:20]}...")
                return True
            else:
                print(f"   ❌ Error en login de admin: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def create_test_user(self):
        """Crear usuario de prueba"""
        print("\n👤 Creando usuario de prueba...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data = {
            "username": f"testuser_{timestamp}",
            "email": f"testuser_{timestamp}@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/register/", json=data)
            if response.status_code == 201:
                result = response.json()
                self.user_id = result.get('user', {}).get('id')
                print(f"   ✅ Usuario creado: {data['email']}")
                print(f"   📄 ID de usuario: {self.user_id}")
                return data['email'], data['password']
            else:
                print(f"   ❌ Error creando usuario: {response.text}")
                return None, None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None, None
    
    def login_test_user(self, email, password):
        """Login del usuario de prueba"""
        print(f"\n🔑 Haciendo login del usuario: {email}")
        
        data = {
            "email": email,
            "password": password
        }
        
        try:
            response = requests.post(f"{BASE_URL}/login/", json=data)
            if response.status_code == 200:
                result = response.json()
                self.user_token = result.get('token')
                print(f"   ✅ Login exitoso: {self.user_token[:20]}...")
                return True
            else:
                print(f"   ❌ Error en login: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_admin_sessions_view(self):
        """Probar vista de administración de sesiones"""
        print("\n📊 Probando vista de administración de sesiones...")
        
        if not self.admin_token:
            print("   ❌ No hay token de administrador")
            return
        
        headers = {"Authorization": f"Token {self.admin_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/admin/sessions/", headers=headers)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Sesiones obtenidas exitosamente")
                print(f"   📈 Total de sesiones: {result['statistics']['total']}")
                print(f"   🟢 Sesiones activas: {result['statistics']['active']}")
                print(f"   🔴 Sesiones inactivas: {result['statistics']['inactive']}")
                print(f"   👥 Usuarios con sesiones: {result['statistics']['users_with_sessions']}")
                
                # Mostrar algunas sesiones
                print("\n   📋 Últimas sesiones:")
                for session in result['sessions'][:3]:
                    status = "🟢 ACTIVA" if session['is_active'] else "🔴 INACTIVA"
                    print(f"      - {session['user']['email']}: {status} (IP: {session['ip_address']})")
                
                return result
            else:
                print(f"   ❌ Error obteniendo sesiones: {response.text}")
                return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def test_user_session_history(self):
        """Probar historial de sesiones del usuario"""
        print(f"\n📜 Probando historial de sesiones del usuario...")
        
        if not self.user_token or not self.user_id:
            print("   ❌ No hay token de usuario o ID")
            return
        
        headers = {"Authorization": f"Token {self.user_token}"}
        
        try:
            # Probar mi historial
            response = requests.get(f"{BASE_URL}/sessions/my-history/", headers=headers)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Mi historial obtenido exitosamente")
                print(f"   📊 Total de sesiones: {result['total_sessions']}")
                print(f"   🟢 Sesiones activas: {result['active_sessions']}")
                
                for session in result['sessions'][:2]:
                    status = "🟢 ACTIVA" if session['is_active'] else "🔴 INACTIVA"
                    print(f"      - {status} (IP: {session['ip_address']}, Duración: {session['duration']})")
                
                return result
            else:
                print(f"   ❌ Error obteniendo mi historial: {response.text}")
                return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def test_admin_user_history(self):
        """Probar historial de sesiones de usuario específico (admin)"""
        print(f"\n👨‍💼 Probando historial de usuario específico (admin)...")
        
        if not self.admin_token or not self.user_id:
            print("   ❌ No hay token de admin o ID de usuario")
            return
        
        headers = {"Authorization": f"Token {self.admin_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/sessions/user/{self.user_id}/", headers=headers)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Historial de usuario obtenido exitosamente")
                print(f"   👤 Usuario: {result['user']['email']}")
                print(f"   📊 Total de sesiones: {result['total_sessions']}")
                print(f"   🟢 Sesiones activas: {result['active_sessions']}")
                
                return result
            else:
                print(f"   ❌ Error obteniendo historial de usuario: {response.text}")
                return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def test_force_logout(self, session_id):
        """Probar logout forzado (admin)"""
        print(f"\n🚪 Probando logout forzado de sesión {session_id}...")
        
        if not self.admin_token:
            print("   ❌ No hay token de administrador")
            return
        
        headers = {"Authorization": f"Token {self.admin_token}"}
        
        try:
            response = requests.delete(f"{BASE_URL}/admin/sessions/{session_id}/", headers=headers)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Logout forzado exitoso: {result['message']}")
                return result
            else:
                print(f"   ❌ Error en logout forzado: {response.text}")
                return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def run_complete_test(self):
        """Ejecutar todas las pruebas"""
        print("🚀 Iniciando pruebas completas de gestión de sesiones")
        print("="*60)
        
        # 1. Setup admin
        if not self.setup_admin_token():
            print("❌ No se pudo obtener token de administrador. Abortando.")
            return
        
        # 2. Crear y hacer login de usuario de prueba
        user_email, user_password = self.create_test_user()
        if not user_email:
            print("❌ No se pudo crear usuario de prueba. Abortando.")
            return
        
        if not self.login_test_user(user_email, user_password):
            print("❌ No se pudo hacer login del usuario de prueba. Abortando.")
            return
        
        # 3. Probar vistas de administración
        admin_sessions = self.test_admin_sessions_view()
        
        # 4. Probar historial del usuario
        self.test_user_session_history()
        
        # 5. Probar historial de usuario específico (admin)
        self.test_admin_user_history()
        
        # 6. Encontrar una sesión activa y hacer logout forzado
        if admin_sessions and admin_sessions['sessions']:
            active_session = next((s for s in admin_sessions['sessions'] if s['is_active']), None)
            if active_session:
                self.test_force_logout(active_session['id'])
                
                # Verificar que el logout forzado funcionó
                print("\n🔍 Verificando logout forzado...")
                self.test_admin_sessions_view()
        
        print("\n" + "="*60)
        print("✅ Pruebas completas de gestión de sesiones finalizadas")

if __name__ == "__main__":
    tester = SessionTester()
    tester.run_complete_test()
