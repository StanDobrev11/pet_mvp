from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from pet_mvp.common.email_service import EmailService


@shared_task
def send_reminder_emails():
    """
    Periodic task to send reminder emails
    This can be scheduled via Celery Beat
    """
    # Example implementation - you would customize this based on your models
    from pet_mvp.records.models import VaccinationRecord
    
    # Find vaccination records that are due in the next 7 days
    upcoming_date = timezone.now().date() + timedelta(days=7)
    upcoming_vaccinations = VaccinationRecord.objects.filter(
        next_vaccination_date=upcoming_date
    )
    
    for record in upcoming_vaccinations:
        # Get pet owner email from your models
        owner_email = record.pet.owner.user.email
        
        # Send reminder email
        EmailService.send_template_email_async.delay(
            subject=f"Vaccination Reminder for {record.pet.name}",
            to_email=owner_email,
            template_name="emails/vaccination_reminder.html",
            context={
                "pet_name": record.pet.name,
                "vaccine": record.vaccine.name,
                "due_date": record.next_vaccination_date,
            }
        )
    
    return f"Processed {upcoming_vaccinations.count()} vaccination reminders"


@shared_task
def send_weekly_report_emails():
    """
    Periodic task to send weekly report emails
    This can be scheduled via Celery Beat
    """
    # Example implementation - you would customize this based on your models
    from pet_mvp.accounts.models import Clinic
    
    for clinic in Clinic.objects.all():
        admin_email = clinic.user.email
        
        # Send weekly report email
        EmailService.send_template_email_async.delay(
            subject=f"Weekly Clinic Report - {timezone.now().strftime('%Y-%m-%d')}",
            to_email=admin_email,
            template_name="emails/weekly_report.html",
            context={
                "clinic_name": clinic.name,
                "report_date": timezone.now().date(),
                # Add other context data as needed
            }
        )
    
    return f"Processed weekly reports for {Clinic.objects.count()} clinics"
