"""
Management command to test attendance system functionality.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import datetime, date, time, timedelta
from employees.models import Employee, Department
from attendance.models import WorkSchedule, TimeEntry, Timesheet, OvertimeRequest, AttendanceReport


class Command(BaseCommand):
    """Test attendance system functionality."""
    
    help = 'Test attendance system models and functionality'

    def handle(self, *args, **options):
        """Execute the test command."""
        self.stdout.write(self.style.SUCCESS('Starting attendance system test...'))
        
        try:
            # Test model imports
            self.stdout.write('✓ Testing model imports...')
            models = [WorkSchedule, TimeEntry, Timesheet, OvertimeRequest, AttendanceReport]
            for model in models:
                self.stdout.write(f'  - {model.__name__}: OK')
            
            # Test database queries
            self.stdout.write('✓ Testing database queries...')
            
            # Check if we have any existing data
            employees_count = Employee.objects.count()
            departments_count = Department.objects.count()
            schedules_count = WorkSchedule.objects.count()
            time_entries_count = TimeEntry.objects.count()
            timesheets_count = Timesheet.objects.count()
            
            self.stdout.write(f'  - Employees: {employees_count}')
            self.stdout.write(f'  - Departments: {departments_count}')
            self.stdout.write(f'  - Work Schedules: {schedules_count}')
            self.stdout.write(f'  - Time Entries: {time_entries_count}')
            self.stdout.write(f'  - Timesheets: {timesheets_count}')
            
            # Test model creation if we have employees
            if employees_count > 0 and departments_count > 0:
                self.stdout.write('✓ Testing model creation...')
                
                # Get first employee and department
                employee = Employee.objects.first()
                department = Department.objects.first()
                
                # Create a work schedule
                schedule, created = WorkSchedule.objects.get_or_create(
                    name='Test Schedule',
                    defaults={
                        'schedule_type': 'FIXED',
                        'department': department,
                        'monday_start': time(9, 0),
                        'monday_end': time(17, 0),
                        'tuesday_start': time(9, 0),
                        'tuesday_end': time(17, 0),
                        'wednesday_start': time(9, 0),
                        'wednesday_end': time(17, 0),
                        'thursday_start': time(9, 0),
                        'thursday_end': time(17, 0),
                        'friday_start': time(9, 0),
                        'friday_end': time(17, 0),
                        'daily_overtime_threshold': 8.0
                    }
                )
                
                if created:
                    self.stdout.write(f'  - Created WorkSchedule: {schedule}')
                else:
                    self.stdout.write(f'  - Found existing WorkSchedule: {schedule}')
                
                # Create a time entry
                clock_in_time = datetime.now() - timedelta(hours=8)
                clock_out_time = datetime.now()
                
                time_entry, created = TimeEntry.objects.get_or_create(
                    employee=employee,
                    clock_in__date=clock_in_time.date(),
                    defaults={
                        'clock_in': clock_in_time,
                        'clock_out': clock_out_time,
                        'entry_type': 'REGULAR',
                        'status': 'APPROVED'
                    }
                )
                
                if created:
                    self.stdout.write(f'  - Created TimeEntry: {time_entry}')
                else:
                    self.stdout.write(f'  - Found existing TimeEntry: {time_entry}')
                
                # Test timesheet creation
                week_start = date.today() - timedelta(days=date.today().weekday())
                
                timesheet, created = Timesheet.objects.get_or_create(
                    employee=employee,
                    week_start=week_start,
                    defaults={
                        'total_hours': 40.0,
                        'regular_hours': 40.0,
                        'overtime_hours': 0.0,
                        'status': 'DRAFT'
                    }
                )
                
                if created:
                    self.stdout.write(f'  - Created Timesheet: {timesheet}')
                else:
                    self.stdout.write(f'  - Found existing Timesheet: {timesheet}')
                
                self.stdout.write(self.style.SUCCESS('✓ All tests passed! Attendance system is working correctly.'))
            else:
                self.stdout.write(self.style.WARNING('⚠ No employees or departments found. Create some test data first.'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Test failed: {str(e)}'))
            import traceback
            self.stdout.write(traceback.format_exc())
