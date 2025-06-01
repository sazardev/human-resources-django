"""
Tests for attendance app.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime, date, time, timedelta
from employees.models import Employee, Department
from .models import WorkSchedule, TimeEntry, Timesheet, OvertimeRequest, AttendanceReport


class AttendanceModelsTest(TestCase):
    """Test attendance models."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create test department
        self.department = Department.objects.create(
            name='Engineering',
            description='Software Engineering Department'
        )
        
        # Create test employee
        self.employee = Employee.objects.create(
            user=self.user,
            employee_id='EMP001',
            department=self.department,
            position='Software Engineer',
            hire_date=date.today(),
            salary=75000.00,
            employment_type='FULL_TIME',
            status='ACTIVE'
        )
    
    def test_work_schedule_creation(self):
        """Test WorkSchedule model creation."""
        schedule = WorkSchedule.objects.create(
            name='Standard Work Week',
            schedule_type='FIXED',
            department=self.department,
            monday_start=time(9, 0),
            monday_end=time(17, 0),
            tuesday_start=time(9, 0),
            tuesday_end=time(17, 0),
            wednesday_start=time(9, 0),
            wednesday_end=time(17, 0),
            thursday_start=time(9, 0),
            thursday_end=time(17, 0),
            friday_start=time(9, 0),
            friday_end=time(17, 0),
            daily_overtime_threshold=8.0
        )
        
        self.assertEqual(schedule.name, 'Standard Work Week')
        self.assertEqual(schedule.department, self.department)
        self.assertTrue(schedule.is_active)
        self.assertEqual(str(schedule), 'Standard Work Week (Engineering)')
    
    def test_time_entry_creation(self):
        """Test TimeEntry model creation."""
        clock_in_time = datetime.now()
        clock_out_time = clock_in_time + timedelta(hours=8)
        
        time_entry = TimeEntry.objects.create(
            employee=self.employee,
            clock_in=clock_in_time,
            clock_out=clock_out_time,
            entry_type='REGULAR',
            status='APPROVED'
        )
        
        self.assertEqual(time_entry.employee, self.employee)
        self.assertEqual(time_entry.entry_type, 'REGULAR')
        self.assertEqual(time_entry.status, 'APPROVED')
        self.assertIsNotNone(time_entry.hours_worked)
    
    def test_timesheet_creation(self):
        """Test Timesheet model creation."""
        week_start = date.today()
        
        timesheet = Timesheet.objects.create(
            employee=self.employee,
            week_start=week_start,
            total_hours=40.0,
            regular_hours=40.0,
            overtime_hours=0.0,
            status='DRAFT'
        )
        
        self.assertEqual(timesheet.employee, self.employee)
        self.assertEqual(timesheet.week_start, week_start)
        self.assertEqual(timesheet.status, 'DRAFT')
        self.assertEqual(timesheet.total_hours, 40.0)
    
    def test_overtime_request_creation(self):
        """Test OvertimeRequest model creation."""
        request_date = date.today()
        
        overtime_request = OvertimeRequest.objects.create(
            employee=self.employee,
            requested_date=request_date,
            estimated_hours=4.0,
            reason='Project deadline',
            status='PENDING'
        )
        
        self.assertEqual(overtime_request.employee, self.employee)
        self.assertEqual(overtime_request.requested_date, request_date)
        self.assertEqual(overtime_request.estimated_hours, 4.0)
        self.assertEqual(overtime_request.status, 'PENDING')
    
    def test_attendance_report_creation(self):
        """Test AttendanceReport model creation."""
        report = AttendanceReport.objects.create(
            title='Monthly Attendance Report',
            report_type='MONTHLY',
            department=self.department,
            start_date=date.today().replace(day=1),
            end_date=date.today(),
            generated_by=self.user,
            report_data={'total_employees': 1}
        )
        
        self.assertEqual(report.title, 'Monthly Attendance Report')
        self.assertEqual(report.report_type, 'MONTHLY')
        self.assertEqual(report.department, self.department)
        self.assertEqual(report.generated_by, self.user)
