from celery import shared_task
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
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
                time_left = _("4 weeks")
            elif interval_name == 'two_weeks':
                time_left = _("2 weeks")
            elif interval_name == 'one_week':
                time_left = _("1 week")
            else:  # expiration_day
                time_left = _("today")

            # Send expiration notification email
            EmailService.send_template_email_async.delay(
                subject=_("Vaccine Expiration Notice for {}").format(
                    record.pet.name),
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

    return _("Processed {} vaccine expiration notifications").format(notifications_sent)


def test_to_dict(test_obj):
    """Convert a test object to a dictionary for JSON serialization"""
    if test_obj is None:
        return None

    return {
        "name": test_obj.name,
        "results": test_obj.result,  # Note: template uses 'results' but model has 'result'
        "notes": test_obj.additional_notes or _("N/A"),
        "date_conducted": test_obj.date_conducted.strftime("%Y-%m-%d") if hasattr(test_obj, 'date_conducted') else None
    }


@shared_task
def send_medical_record_email(exam):
    """task to send one-time notification on creation of a medical record to owners"""

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
        "general_health": exam.general_health or _("N/A"),
        "body_condition_score": exam.body_condition_score,
        "temperature": exam.temperature,
        "heart_rate": exam.heart_rate,
        "respiratory_rate": exam.respiratory_rate,
        "treatment_performed": exam.treatment_performed,
        "diagnosis": exam.diagnosis or _("N/A"),
        "follow_up": _("Yes") if exam.follow_up else _("No"),
        "notes": exam.notes or _("N/A"),
        "vaccinations": [
            {"name": v.vaccine.name,
                "date": v.date_of_vaccination.strftime("%Y-%m-%d")}
            for v in exam.vaccinations.all()
        ],
        "medications": [
            {"name": m.medication.name, "dosage": m.dosage}
            for m in exam.medications.all()
        ],
        # Convert test objects to dictionaries for JSON serialization
        'blood_test': test_to_dict(getattr(exam, 'blood_test', None)),
        'urine_test': test_to_dict(getattr(exam, 'urine_test', None)),
        'fecal_test': test_to_dict(getattr(exam, 'fecal_test', None)),

    }

    EmailService.send_template_email_async.delay(
        subject=_("Medical Examination Report for {} - {}").format(exam.pet.name,
                                                                   exam.date_of_entry.strftime('%Y-%m-%d')),
        to_email=owners_emails,
        template_name='emails/medical_report_email.html',
        context=context
    )

    return _("Processed one medical report for {}").format(exam.pet.name)


@shared_task
def send_user_registration_email(user):
    """task to send one-time notification on creation of a medical record"""

    user_email = user.email

    if user.is_owner:
        context = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user_email,
            "password": user.password,
            "username": user.username
        }
        EmailService.send_template_email_async.delay(
            subject=_("Welcome {} {}").format(user.first_name, user.last_name),
            to_email=user_email,
            template_name='emails/user_registration_email.html',
            context=context
        )
