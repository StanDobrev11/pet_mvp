from celery import shared_task
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from pet_mvp.notifications.email_service import EmailService

UserModel = get_user_model()

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
    
    for user in UserModel.objects.all():

        if user.is_owner:
            user_email = user.email

            # Send weekly report email
            EmailService.send_template_email_async.delay(
                subject=f"Weekly Clinic Report - {timezone.now().strftime('%Y-%m-%d')}",
                to_email=user_email,
                template_name='emails/weekly_report.html',
                context={
                    "vaccine_due": 'some vaccine',
                    "report_date": timezone.now().date(),
                    # Add other context data as needed
                }
            )
    
    return f"Processed weekly reports for {Clinic.objects.count()} clinics"


@shared_task
def send_medical_record_email(exam):
    """task to send one-time notification on creation of a medical record"""

    # get the owners emails of the pet
    owners_emails = [owner.email for owner in exam.pet.owners.all()]

    clinic = exam.clinic
    context = {
            "pet_name": exam.pet.name,
            "date_of_entry": exam.date_of_entry.strftime("%Y-%m-%d"),
            "doctor": exam.doctor,
            "clinic_name": clinic.clinic_name,
            "clinic_address": clinic.clinic_address,
            "clinic_city": clinic.city,
            "clinic_country": clinic.country,
            "clinic_phone": clinic.phone_number,
            "reason_for_visit": exam.reason_for_visit,
            "general_health": exam.general_health,
            "body_condition_score": exam.body_condition_score,
            "temperature": exam.temperature,
            "heart_rate": exam.heart_rate,
            "respiratory_rate": exam.respiratory_rate,
            "treatment_performed": exam.treatment_performed,
            "diagnosis": exam.diagnosis,
            "follow_up": "Yes" if exam.follow_up else "No",
            "notes": exam.notes or "N/A",
            "vaccinations": [
                {"name": v.vaccine_type, "date": v.date.strftime("%Y-%m-%d")}
                for v in exam.vaccinations.all()
            ],
            "medications": [
                {"name": m.name, "dosage": m.dosage}
                for m in exam.medications.all()
            ],
        }

    EmailService.send_template_email_async.delay(
        subject=f"Medical Examination Report for {exam.pet.name} - {exam.date_of_entry.strftime('%Y-%m-%d')}",
        to_email=owners_emails,
        template_name='emails/medical_report_email.html',
        context=context
    )

    return f"Processed one medical report for {exam.pet.name}"