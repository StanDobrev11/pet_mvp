from celery import shared_task
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from pet_mvp.notifications.email_service import EmailService

UserModel = get_user_model()

@shared_task
def send_vaccine_expiration_notifications():
    """
    Periodic task to send vaccine expiration notifications
    Checks for vaccines expiring in 4 weeks, 2 weeks, 1 week, and on the expiration date
    This can be scheduled via Celery Beat
    """
    from pet_mvp.records.models import VaccinationRecord

    today = timezone.now().date()

    # Define notification intervals
    intervals = {
        'four_weeks': today + timedelta(days=28),
        'two_weeks': today + timedelta(days=14),
        'one_week': today + timedelta(days=7),
        'expiration_day': today
    }

    notifications_sent = 0

    for interval_name, check_date in intervals.items():
        # Find vaccination records that expire on the check date
        expiring_vaccinations = VaccinationRecord.objects.filter(
            valid_until=check_date
        )

        for record in expiring_vaccinations:
            # Get pet owners' emails
            owners_emails = [owner.email for owner in record.pet.owners.all()]

            # Prepare notification message based on interval
            if interval_name == 'four_weeks':
                time_left = "4 weeks"
            elif interval_name == 'two_weeks':
                time_left = "2 weeks"
            elif interval_name == 'one_week':
                time_left = "1 week"
            else:  # expiration_day
                time_left = "today"

            # Send expiration notification email
            EmailService.send_template_email_async.delay(
                subject=f"Vaccine Expiration Notice for {record.pet.name}",
                to_email=owners_emails,
                template_name="emails/vaccine_expiration_notification.html",
                context={
                    "pet_name": record.pet.name,
                    "vaccine": record.vaccine.name,
                    "expiration_date": record.valid_until,
                    "time_left": time_left
                }
            )

            notifications_sent += 1

    return f"Processed {notifications_sent} vaccine expiration notifications"


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
        "general_health": exam.general_health or "N/A",
        "body_condition_score": exam.body_condition_score,
        "temperature": exam.temperature,
        "heart_rate": exam.heart_rate,
        "respiratory_rate": exam.respiratory_rate,
        "treatment_performed": exam.treatment_performed,
        "diagnosis": exam.diagnosis or "N/A",
        "follow_up": "Yes" if exam.follow_up else "No",
        "notes": exam.notes or "N/A",
        "vaccinations": [
            {"name": v.vaccine.name, "date": v.date_of_vaccination.strftime("%Y-%m-%d")}
            for v in exam.vaccinations.all()
        ],
        "medications": [
            {"name": m.medication.name, "dosage": m.dosage}
            for m in exam.medications.all()
        ],
        # these must be included explicitly:
        'blood_test': getattr(exam, 'blood_test', None),
        'urine_test': getattr(exam, 'urine_test', None),
        'fecal_test': getattr(exam, 'fecal_test', None),

    }

    EmailService.send_template_email_async.delay(
        subject=f"Medical Examination Report for {exam.pet.name} - {exam.date_of_entry.strftime('%Y-%m-%d')}",
        to_email=owners_emails,
        template_name='emails/medical_report_email.html',
        context=context
    )

    return f"Processed one medical report for {exam.pet.name}"
