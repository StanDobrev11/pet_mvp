import os

from celery import shared_task
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from pet_mvp.notifications.email_service import EmailService


UserModel = get_user_model()

@shared_task
def send_clinic_owner_access_request_email(user_owner, user_clinic, pet, url, lang):

    context = {
        "owner_name": user_owner.get_full_name(),
        "clinic_name": user_clinic.clinic.name,
        "clinic_email": user_clinic.email,
        "clinic_phone": user_clinic.phone_number,
        "clinic_city": user_clinic.city,
        "clinic_country": user_clinic.country,
        "pet_name": pet.name,
        "approval_url": url,
        "lang": lang,
    }

    subject = _("Approval Request for Access to {{ pet_name }}'s Medical Records").replace(
        "{{ pet_name }}", pet.name
    )

    EmailService.send_template_email_async(
        subject=subject,
        to_email=user_owner.email,
        template_name="emails/clinic_owner_access_request_email.html",
        context=context,
    )

# sending email to the admin for review of the clinic and mark as approved
@shared_task
def send_clinic_admin_approval_request_email(user_clinic, pet):

    context = {
        "clinic_name": user_clinic.clinic.name,
        "clinic_email": user_clinic.email,
        "clinic_phone": user_clinic.phone_number,
        "clinic_city": user_clinic.city,
        "clinic_country": user_clinic.country,
        "pet_name": pet.name,
    }

    EmailService.send_template_email_async(
        subject=_("Clinic approval request: {}").format(user_clinic.clinic.name),
        to_email=os.getenv("ADMIN_EMAIL"),
        template_name='emails/clinic_admin_approval_request_email.html',
        context=context
    )

@shared_task
def send_treatment_expiration_notifications():
    """
    Periodic task to send treatment expiration notifications.
    Sends notifications 7 days and 1 day before the 'valid_until' date.
    """
    from pet_mvp.records.models import MedicationRecord

    today = timezone.now().date()

    intervals = {
        'one_week': today + timedelta(days=7),
        'one_day': today + timedelta(days=1),
    }

    notifications_sent = 0

    for interval_name, check_date in intervals.items():
        expiring_treatments = MedicationRecord.objects.filter(
            valid_until=check_date
        )

        for record in expiring_treatments:
            user_owners = record.pet.owners.all()

            time_left = _("in 1 week") if interval_name == 'one_week' else _("tomorrow")
            
            for user in user_owners:
                EmailService.send_template_email_async.delay(
                    subject=_("Treatment Expiration Reminder for {}").format(
                        record.pet.name),
                    to_email=user.email,
                    template_name="emails/treatment_expiration_notification.html",
                    context={
                        "pet_name": record.pet.name,
                        "medication": record.medication.name,
                        "expiration_date": record.valid_until,
                        "time_left": time_left,
                        "lang": user.default_language,
                    }
                )
                notifications_sent += 1

    return _("Processed {} treatment expiration notifications").format(notifications_sent)

@shared_task
def send_wrong_vaccination_report(owner_id, vaccine_record_id, url):
    """
    One-time notification sent to the admin to reset a wrongly entered vaccination.
    """
    from django.contrib.auth import get_user_model
    from pet_mvp.records.models import VaccinationRecord

    User = get_user_model()
    owner = User.objects.get(pk=owner_id)
    vaccine_record = VaccinationRecord.objects.get(pk=vaccine_record_id)

    context = {
        'owner_name': owner.get_full_name(),
        'vaccine_name': vaccine_record.vaccine.name,
        'url': url,
    }

    EmailService.send_template_email_async(
        subject=_("Vaccine reset request"),
        to_email=os.getenv("ADMIN_EMAIL"),
        template_name='emails/vaccine_reset_request_email.html',
        context=context
    )

    return _("Processed vaccine reset")

@shared_task
def send_vaccine_expiration_notifications():
    """
    Periodic task to send vaccine expiration notifications.
    Checks for vaccines expiring in 4 weeks, 2 weeks, 1 week, and 1 day before expiration.
    Intended to be scheduled via Celery Beat.
    """
    from pet_mvp.records.models import VaccinationRecord

    today = timezone.now().date()

    intervals = {
        'four_weeks': (today + timedelta(days=28), _("in 4 weeks")),
        'two_weeks': (today + timedelta(days=14), _("in 2 weeks")),
        'one_week': (today + timedelta(days=7), _("in 1 week")),
        'one_day': (today + timedelta(days=1), _("tomorrow")),
    }

    notifications_sent = 0

    for label, (check_date, time_left) in intervals.items():
        expiring_vaccinations = VaccinationRecord.objects.filter(
            valid_until=check_date)

        for record in expiring_vaccinations:
            for user in record.pet.owners.all():
                EmailService.send_template_email_async.delay(
                    subject=_("Vaccine Expiration Notice for {}").format(
                        record.pet.name),
                    to_email=user.email,
                    template_name="emails/vaccine_expiration_notification.html",
                    context={
                        "pet_name": record.pet.name,
                        "vaccine": record.vaccine.name,
                        "expiration_date": record.valid_until,
                        "time_left": time_left,
                        "lang": user.default_language,
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
def send_medical_record_email(exam, lang):
    """task to send one-time notification on creation of a medical record to owners and the clinic"""

    # get owners' details
    owners_details = [user for user in exam.pet.owners.all()]

    owner_details = [{
        "first_name": user.owner.first_name,
        "last_name": user.owner.last_name,
        "email": user.email,
        "phone_number": user.phone_number,
        "city": user.city,
        "country": user.country
    } for user in owners_details]

    # get the owners emails of the pet
    owners_emails = [owner.email for owner in owners_details]

    user_clinic = exam.clinic
    context = {
        "owners": owner_details,
        "pet_name": exam.pet.name,
        "date_of_entry": exam.date_of_entry.strftime("%Y-%m-%d"),
        "doctor": exam.doctor,
        "clinic_name": user_clinic.clinic.name,
        "clinic_address": user_clinic.clinic.address,
        "clinic_city": user_clinic.city,
        "clinic_country": user_clinic.country,
        "clinic_phone": user_clinic.phone_number,
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
        "lang": lang,
    }

    EmailService.send_template_email_async.delay(
        subject=_("Medical Examination Report for {} - {}").format(exam.pet.name,
                                                                   exam.date_of_entry.strftime('%Y-%m-%d')),
        to_email=owners_emails,
        template_name='emails/medical_report_email.html',
        context=context
    )

    if user_clinic.default_language != lang:
        context['lang'] = user_clinic.default_language

    EmailService.send_template_email_async.delay(
        subject=_("Medical Examination Report for {} - {}").format(exam.pet.name,
                                                                   exam.date_of_entry.strftime('%Y-%m-%d')),
        to_email=user_clinic.email,
        template_name='emails/medical_report_email.html',
        context=context
    )

    return _("Processed one medical report for {}").format(exam.pet.name)


@shared_task
def send_user_registration_email(user, lang):
    """
    Task to send a one-time notification on registration of a user.
    - For owners: sends a welcome email.
    - For clinics: sends a notification for registration email.
    """

    user_email = user.email

    # Send owner welcome email
    if user.is_owner:
        context = {
            "first_name": user.owner.first_name,
            "last_name": user.owner.last_name,
            "lang": lang,
        }
        EmailService.send_template_email_async.delay(
            subject=_("Welcome {} {}").format(user.owner.first_name, user.owner.last_name),
            to_email=user_email,
            template_name='emails/user_registration_email.html',
            context=context,
        )
        return _("Sent registration email to {}").format(user_email)

    # Send clinic registration notification email

    context = {
        "clinic_name": user.clinic.name,
        "clinic_address": user.clinic.address,
        "clinic_email": user.email,
        "clinic_country": user.country,
        "city": user.city,
        "phone_number": user.phone_number,
        "admin_email": os.getenv("ADMIN_EMAIL"),
    }

    EmailService.send_template_email_async.delay(
        subject=_("Activate your clinic account: {}").format(user.name),
        to_email=user_email,
        template_name='emails/clinic_registration_notification_email.html',
        context=context,
    )
    return _("Sent clinic notification email to {}").format(user_email)

@shared_task
def send_clinic_activation_email(user, lang, url):
    # send clinic activation email

    user_email = user.email
        
    context = {
        "clinic_email": user_email,
        "clinic_name": user.clinic.name,
        "clinic_address": user.clinic.address,
        "city": user.city,
        "country": user.country,
        "phone_number": user.phone_number,
        "activation_url": url,
        "lang": lang,
    }

    EmailService.send_template_email_async.delay(
        subject=_("Activation confirmation email"),
        to_email=user_email,
        template_name='emails/clinic_activation_email.html',
        context=context
    )
    return _("Sent activation email to {}").format(user_email)


@shared_task
def send_owner_pet_addition_request(existing_owner, new_owner, pet, approval_url):

    context = {
        "first_name": new_owner.owner.first_name,
        "last_name": new_owner.owner.last_name,
        "lang": existing_owner.default_language,
        "pet_name": pet.name,
        "pet_passport": pet.passport_number,
        "approval_url": approval_url,
    }

    EmailService.send_template_email_async.delay(
        subject=_('Pet Addition Request'),
        to_email=existing_owner.email,
        template_name='emails/pet_add_request_email.html',
        context=context
    )
