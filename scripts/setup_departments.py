#!/usr/bin/env python
"""
Script simple para crear departamentos y mejorar datos de empleados
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from employees.models import Employee, Department
from authentication.models import User
from decimal import Decimal
import random

def main():
    print("🏢 CREANDO DATOS DE PRUEBA REALISTAS")
    print("=" * 50)
    
    # 1. Crear departamentos
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
    
    # 2. Actualizar empleados existentes
    employees = Employee.objects.all()
    print(f"\n👥 Actualizando {employees.count()} empleados...")
    
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
    
    dept_names = list(departments.keys())
    
    for i, employee in enumerate(employees):
        # Asignar departamento de manera distribuida
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
        employee.save()
        
        print(f"  ✅ {employee.employee_id}: {employee.first_name} {employee.last_name}")
        print(f"     Departamento: {employee.department.name}")
        print(f"     Posición: {employee.position}")
        print(f"     Salario: ${employee.salary:,.2f}")
    
    # 3. Estadísticas finales
    print(f"\n📊 ESTADÍSTICAS FINALES:")
    print(f"Departamentos: {Department.objects.count()}")
    print(f"Empleados: {Employee.objects.count()}")
    
    print(f"\n🏢 EMPLEADOS POR DEPARTAMENTO:")
    for dept in Department.objects.all():
        count = dept.employee_set.count()
        print(f"  {dept.name}: {count} empleados")
    
    print("\n🎉 ¡Datos actualizados exitosamente!")

if __name__ == "__main__":
    main()
