#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from authentication.models import User
from employees.models import Employee, Department

def analyze_user_employee_relationship():
    """Analizar la relación entre User y Employee"""
    
    print("📊 ANÁLISIS: USER vs EMPLOYEE")
    print("=" * 50)
    
    # Obtener datos
    users = User.objects.all()
    employees = Employee.objects.all()
    departments = Department.objects.all()
    
    print(f"👥 USUARIOS TOTALES: {users.count()}")
    print(f"💼 EMPLEADOS TOTALES: {employees.count()}")
    print(f"🏢 DEPARTAMENTOS TOTALES: {departments.count()}")
    
    print("\n🔍 ANÁLISIS DE USUARIOS:")
    print("-" * 30)
    
    users_with_employee = 0
    users_without_employee = 0
    
    for user in users:
        try:
            employee = user.employee_profile
            users_with_employee += 1
            print(f"✅ {user.email} -> Empleado ID: {employee.employee_id}")
        except Employee.DoesNotExist:
            users_without_employee += 1
            print(f"❌ {user.email} -> SIN perfil de empleado")
    
    print(f"\n📈 RESUMEN:")
    print(f"Usuarios CON perfil de empleado: {users_with_employee}")
    print(f"Usuarios SIN perfil de empleado: {users_without_employee}")
    
    print(f"\n🏢 DEPARTAMENTOS:")
    for dept in departments:
        emp_count = dept.employee_set.count()
        print(f"  {dept.name}: {emp_count} empleados")
    
    # Problema identificado
    print(f"\n🚨 PROBLEMA IDENTIFICADO:")
    if users_without_employee > 0:
        print(f"Hay {users_without_employee} usuarios sin perfil de empleado.")
        print("Esto explica por qué no ves actividad en Employee admin.")
        print("\n💡 SOLUCIÓN RECOMENDADA:")
        print("1. Crear perfiles de Employee para usuarios existentes")
        print("2. O implementar auto-creación de Employee al registrar User")
    else:
        print("Todos los usuarios tienen perfil de empleado.")

if __name__ == "__main__":
    analyze_user_employee_relationship()
