"""
Signal handlers for attendance app.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import TimeEntry, Timesheet


@receiver(pre_save, sender=TimeEntry)
def calculate_time_entry_hours(sender, instance, **kwargs):
    """
    Calculate hours worked and overtime status when saving TimeEntry.
    """
    if instance.clock_in and instance.clock_out:
        # Calculate total time worked
        time_diff = instance.clock_out - instance.clock_in
        total_hours = time_diff.total_seconds() / 3600
        
        # Subtract break duration if specified
        if instance.break_duration:
            break_hours = instance.break_duration.total_seconds() / 3600
            total_hours -= break_hours
        
        # Store original hours if this is the first calculation
        if not instance.original_hours:
            instance.original_hours = Decimal(str(round(max(0, total_hours), 2)))
        
        # Check if this is overtime based on daily threshold
        if total_hours > 8:
            instance.entry_type = 'overtime'


@receiver(post_save, sender=TimeEntry)
def update_timesheet_on_time_entry_save(sender, instance, created, **kwargs):
    """
    Update related timesheet when a time entry is saved.
    """
    if instance.clock_in:
        # Get the Monday of the week for this time entry
        date = instance.clock_in.date()
        week_start = date - timedelta(days=date.weekday())
        
        # Find or create timesheet for this week
        timesheet, created = Timesheet.objects.get_or_create(
            employee=instance.employee,
            week_start=week_start,
            defaults={
                'week_end': week_start + timedelta(days=6),
                'status': 'draft'
            }
        )
        
        # Recalculate timesheet totals
        timesheet.calculate_totals()


@receiver(post_save, sender=Timesheet)
def timesheet_status_change(sender, instance, created, **kwargs):
    """
    Handle timesheet status changes.
    """
    if not created and instance.status == 'approved':
        # When timesheet is approved, approve all related time entries
        time_entries = instance.time_entries.filter(status='completed')
        time_entries.update(status='approved')
        
        # Set approval timestamp
        if not instance.approved_at:
            instance.approved_at = timezone.now()
            Timesheet.objects.filter(pk=instance.pk).update(approved_at=instance.approved_at)
