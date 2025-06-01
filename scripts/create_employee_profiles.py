#!/usr/bin/env python
"""
Script para crear perfiles de Employee para usuarios existentes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from authentication.models import User
from employees.models import Employee, Department
from datetime import date

def create_employee_profiles():
    """Crear perfiles de Employee para usuarios existentes"""
    
    print("🔧 CREANDO PERFILES DE EMPLOYEE")
    print("=" * 40)
    
    # Crear departamento por defecto si no existe
    default_dept, created = Department.objects.get_or_create(
        name="General",
        defaults={"description": "Departamento general para empleados sin departamento específico"}
    )
    
    if created:
        print(f"✅ Departamento '{default_dept.name}' creado")
    
    users_without_employee = User.objects.filter(employee_profile__isnull=True)
    
    print(f"👥 Usuarios sin perfil de empleado: {users_without_employee.count()}")
    
    for user in users_without_employee:
        try:
            # Generar employee_id único
            employee_id = f"EMP{str(user.id).zfill(4)}"
            
            employee = Employee.objects.create(
                user=user,
                employee_id=employee_id,
                first_name=user.first_name or "Sin nombre",
                last_name=user.last_name or "Sin apellido", 
                email=user.email,
                phone=user.phone or "",
                department=default_dept,
                position="Empleado General",
                hire_date=user.date_joined.date() if user.date_joined else date.today(),
                employment_status="active"
            )
            
            print(f"✅ Perfil de empleado creado para {user.email} (ID: {employee_id})")
            
        except Exception as e:
            print(f"❌ Error creando perfil para {user.email}: {e}")
    
    print(f"\n📊 RESULTADO FINAL:")
    print(f"Usuarios totales: {User.objects.count()}")
    print(f"Empleados totales: {Employee.objects.count()}")
    print(f"Departamentos: {Department.objects.count()}")

if __name__ == "__main__":
    create_employee_profiles()
