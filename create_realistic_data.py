#!/usr/bin/env python
"""
Script para crear datos de prueba más realistas
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from employees.models import Employee, Department
from authentication.models import User
from decimal import Decimal
import random

def create_realistic_test_data():
    """Crear datos de prueba más realistas"""
    
    print("🏢 CREANDO DATOS DE PRUEBA REALISTAS")
    print("=" * 50)
    
    # 1. Crear departamentos reales
    departments_data = [
        ("Recursos Humanos", "Gestión del talento humano y bienestar laboral"),
        ("Desarrollo", "Desarrollo de software y tecnología"),
        ("Marketing", "Estrategias de marketing y comunicación"),
        ("Ventas", "Gestión de ventas y relaciones con clientes"),
        ("Finanzas", "Gestión financiera y contabilidad"),
        ("Operaciones", "Operaciones y logística empresarial")
    ]
    
    print("📂 Creando departamentos...")
    departments = {}
    for name, desc in departments_data:
        dept, created = Department.objects.get_or_create(
            name=name,
            defaults={"description": desc}
        )
        departments[name] = dept
        status = "✅ Creado" if created else "📋 Existente"
        print(f"  {status}: {name}")
    
    # 2. Actualizar empleados existentes con datos realistas
    employees = Employee.objects.all()
    print(f"\n👥 Actualizando {employees.count()} empleados...")
    
    # Datos de ejemplo más realistas
    positions_by_dept = {
        "Recursos Humanos": ["HR Manager", "HR Specialist", "Recruiter"],
        "Desarrollo": ["Senior Developer", "Full Stack Developer", "DevOps Engineer"],
        "Marketing": ["Marketing Manager", "Digital Marketing Specialist", "Content Creator"],
        "Ventas": ["Sales Manager", "Sales Representative", "Account Executive"],
        "Finanzas": ["Financial Manager", "Accountant", "Financial Analyst"],
        "Operaciones": ["Operations Manager", "Project Manager", "Operations Coordinator"]
    }
    
    salary_ranges = {
        "Manager": (80000, 120000),
        "Senior": (60000, 90000),
        "Specialist": (45000, 70000),
        "Representative": (35000, 55000),
        "Coordinator": (40000, 60000),
        "Analyst": (50000, 75000),
        "Engineer": (55000, 85000),
        "Developer": (50000, 80000)
    }
    
    for i, employee in enumerate(employees):
        # Asignar departamento de manera distribuida
        dept_names = list(departments.keys())
        if i == 0:  # Admin como HR Manager
            dept_name = "Recursos Humanos"
            position = "HR Manager"
        else:
            dept_name = dept_names[i % len(dept_names)]
            positions = positions_by_dept[dept_name]
            position = positions[i % len(positions)]
        
        # Calcular salario basado en posición
        salary = 50000  # Default
        for key, (min_sal, max_sal) in salary_ranges.items():
            if key in position:
                salary = random.randint(min_sal, max_sal)
                break
        
        # Actualizar empleado
        employee.department = departments[dept_name]
        employee.position = position
        employee.salary = Decimal(str(salary))
        
        # Mejorar nombres si son genéricos
        if employee.first_name in ["Usuario", "Sin nombre"]:
            names = ["Ana", "Carlos", "María", "Luis", "Sofia", "Diego"]
            employee.first_name = names[i % len(names)]
        
        if employee.last_name in ["Test", "Sin apellido"]:
            surnames = ["García", "Rodríguez", "López", "Martínez", "González", "Pérez"]
            employee.last_name = surnames[i % len(surnames)]
        
        employee.save()
        
        print(f"  ✅ {employee.employee_id}: {employee.first_name} {employee.last_name}")
        print(f"     Departamento: {employee.department.name}")
        print(f"     Posición: {employee.position}")
        print(f"     Salario: ${employee.salary:,.2f}")
        print()
    
    # 3. Estadísticas finales
    print("📊 ESTADÍSTICAS FINALES:")
    print("-" * 30)
    print(f"Departamentos creados: {Department.objects.count()}")
    print(f"Empleados actualizados: {Employee.objects.count()}")
    
    print(f"\n🏢 EMPLEADOS POR DEPARTAMENTO:")
    for dept in Department.objects.all():
        count = dept.employee_set.count()
        print(f"  {dept.name}: {count} empleados")
    
    print(f"\n💰 RANGO SALARIAL:")
    salaries = Employee.objects.filter(salary__isnull=False).values_list('salary', flat=True)
    if salaries:
        min_salary = min(salaries)
        max_salary = max(salaries)
        avg_salary = sum(salaries) / len(salaries)
        print(f"  Mínimo: ${min_salary:,.2f}")
        print(f"  Máximo: ${max_salary:,.2f}")
        print(f"  Promedio: ${avg_salary:,.2f}")
    
    print("\n🎉 ¡Datos de prueba realistas creados exitosamente!")
    print("Ahora puedes ver la diferencia entre User y Employee en el admin.")

if __name__ == "__main__":
    create_realistic_test_data()
