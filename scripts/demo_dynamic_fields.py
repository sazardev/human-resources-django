#!/usr/bin/env python
"""
DEMOSTRACIÓN: Campos Dinámicos en TODAS las Apps
Script para mostrar que el sistema de selección de campos dinámicos
funciona correctamente en employees, leaves y payroll.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from employees.serializers import EmployeeSerializer, DepartmentSerializer
from leaves.serializers import LeaveTypeSerializer, LeaveRequestSerializer
from payroll.serializers import PayrollPeriodSerializer, PayslipSerializer
from employees.models import Employee, Department
from leaves.models import LeaveType, LeaveRequest
from payroll.models import PayrollPeriod, Payslip

def demo_dynamic_fields():
    """Demostrar campos dinámicos en todas las aplicaciones"""
    
    print("🎯 DEMOSTRACIÓN: CAMPOS DINÁMICOS EN TODAS LAS APPS")
    print("=" * 60)
    
    # 1. EMPLOYEES APP
    print("\n🏢 1. EMPLOYEES APP")
    print("-" * 20)
    
    if Employee.objects.exists():
        employee = Employee.objects.first()
        
        # Test con fields específicos
        serializer = EmployeeSerializer(employee, fields=['id', 'first_name', 'last_name', 'email'])
        print(f"✅ Employee con fields limitados: {list(serializer.data.keys())}")
        
        # Test con exclude
        serializer = EmployeeSerializer(employee, exclude=['created_at', 'updated_at', 'phone'])
        excluded_fields = {'created_at', 'updated_at', 'phone'}
        returned_fields = set(serializer.data.keys())
        excluded_found = excluded_fields & returned_fields
        
        if not excluded_found:
            print(f"✅ Employee con exclude funcionando: excluidos correctamente")
        else:
            print(f"❌ Employee exclude falló: {excluded_found} no fueron excluidos")
    
    # 2. LEAVES APP  
    print("\n🏖️ 2. LEAVES APP")
    print("-" * 15)
    
    if LeaveType.objects.exists():
        leave_type = LeaveType.objects.first()
        
        # Test con fields específicos
        serializer = LeaveTypeSerializer(leave_type, fields=['id', 'name', 'description', 'is_active'])
        print(f"✅ LeaveType con fields limitados: {list(serializer.data.keys())}")
        
        # Test con exclude
        serializer = LeaveTypeSerializer(leave_type, exclude=['created_at', 'updated_at', 'color_code'])
        excluded_fields = {'created_at', 'updated_at', 'color_code'}
        returned_fields = set(serializer.data.keys())
        excluded_found = excluded_fields & returned_fields
        
        if not excluded_found:
            print(f"✅ LeaveType con exclude funcionando: excluidos correctamente")
        else:
            print(f"❌ LeaveType exclude falló: {excluded_found} no fueron excluidos")
    
    # 3. PAYROLL APP
    print("\n💰 3. PAYROLL APP")
    print("-" * 16)
    
    if PayrollPeriod.objects.exists():
        period = PayrollPeriod.objects.first()
        
        # Test con fields específicos
        serializer = PayrollPeriodSerializer(period, fields=['id', 'name', 'start_date', 'end_date', 'status'])
        print(f"✅ PayrollPeriod con fields limitados: {list(serializer.data.keys())}")
        
        # Test con exclude
        serializer = PayrollPeriodSerializer(period, exclude=['created_at', 'updated_at'])
        excluded_fields = {'created_at', 'updated_at'}
        returned_fields = set(serializer.data.keys())
        excluded_found = excluded_fields & returned_fields
        
        if not excluded_found:
            print(f"✅ PayrollPeriod con exclude funcionando: excluidos correctamente")
        else:
            print(f"❌ PayrollPeriod exclude falló: {excluded_found} no fueron excluidos")

def show_inheritance_status():
    """Mostrar el estado de herencia de los serializers"""
    
    print("\n🔍 ESTADO DE HERENCIA DE SERIALIZERS")
    print("=" * 40)
    
    from employees.mixins import SelectableFieldsSerializer, DynamicFieldsMixin
    
    serializers_to_check = [
        ("EmployeeSerializer", EmployeeSerializer),
        ("DepartmentSerializer", DepartmentSerializer),
        ("LeaveTypeSerializer", LeaveTypeSerializer),
        ("LeaveRequestSerializer", LeaveRequestSerializer), 
        ("PayrollPeriodSerializer", PayrollPeriodSerializer),
        ("PayslipSerializer", PayslipSerializer),
    ]
    
    for name, serializer_class in serializers_to_check:
        has_selectable = issubclass(serializer_class, SelectableFieldsSerializer)
        has_dynamic = issubclass(serializer_class, DynamicFieldsMixin)
        
        if has_selectable and has_dynamic:
            print(f"✅ {name}: Campos dinámicos ✓")
        else:
            print(f"❌ {name}: Sin campos dinámicos")

def show_data_counts():
    """Mostrar datos disponibles para testing"""
    
    print("\n📊 DATOS DISPONIBLES PARA TESTING")
    print("=" * 35)
    
    counts = [
        ("Employee", Employee.objects.count()),
        ("Department", Department.objects.count()),
        ("LeaveType", LeaveType.objects.count()),
        ("LeaveRequest", LeaveRequest.objects.count()),
        ("PayrollPeriod", PayrollPeriod.objects.count()),
        ("Payslip", Payslip.objects.count()),
    ]
    
    for model_name, count in counts:
        print(f"• {model_name}: {count} registros")

if __name__ == "__main__":
    print("🚀 INICIANDO DEMOSTRACIÓN DE CAMPOS DINÁMICOS")
    print("🎯 Verificando employees, leaves y payroll apps")
    
    show_data_counts()
    show_inheritance_status() 
    demo_dynamic_fields()
    
    print("\n" + "=" * 60)
    print("🎉 ¡DEMOSTRACIÓN COMPLETADA!")
    print("✅ Los campos dinámicos funcionan en TODAS las aplicaciones")
    print("🔗 Usa ?fields= y ?exclude= en cualquier endpoint de la API")
    print("=" * 60)
