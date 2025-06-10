"""
Test cases for medical record email notifications.

This module contains tests for the send_medical_record_email task.
"""
from django.test import TestCase
from django.utils import timezone
from django.utils.translation import gettext as _
from datetime import timedelta
from unittest.mock import patch

from pet_mvp.notifications.tasks import send_medical_record_email
from pet_mvp.records.models import MedicalExaminationRecord
from pet_mvp.pets.models import Pet
from django.contrib.auth import get_user_model

User = get_user_model()


class MedicalRecordEmailTestCase(TestCase):
    """Test cases for medical record email notifications."""

    def setUp(self):
        """Set up test data."""
        # Create a test owner
        self.test_owner = User.objects.create_owner(
            email='owner@example.com',
            password='testpassword',
            first_name='Test',
            last_name='Owner',
            phone_number='1234567890',
            city='Test City',
            country='Test Country',
            is_owner=True,
        )

        # Create a test clinic
        self.test_clinic = User.objects.create_clinic(
            email='clinic@example.com',
            password='testpassword',
            clinic_name='Test Clinic',
            clinic_address='123 Test St',
            city='Test City',
            country='Test Country',
            phone_number='0987654321',
        )

        # Create a test pet
        self.test_pet = Pet.objects.create(
            name='TestPet',
            species='Dog',
            breed='Mixed',
            sex='male',
            date_of_birth=timezone.now().date() - timedelta(days=365),
            color='Brown',
            features='Test pet for medical record emails',
            current_weight=10.0,
            passport_number='TEST12345678',
        )
        self.test_pet.owners.add(self.test_owner)

        # Create a test medical examination record
        self.test_exam = MedicalExaminationRecord.objects.create(
            exam_type='primary',
            date_of_entry=timezone.now().date(),
            doctor='Dr. Test',
            clinic=self.test_clinic,
            pet=self.test_pet,
            reason_for_visit='Annual checkup',
            general_health='Good',
            body_condition_score=5,
            temperature=38.5,
            heart_rate=80,
            respiratory_rate=20,
            treatment_performed='General examination',
            diagnosis='Healthy',
            follow_up=False,
            notes='No issues found',
        )

    @patch('pet_mvp.notifications.email_service.EmailService.send_template_email_async')
    def test_send_medical_record_email(self, mock_send_email):
        """Test that medical record email is sent correctly."""
        # Run the task
        result = send_medical_record_email(self.test_exam, 'bg')

        # Check that the task processed the medical report
        self.assertIn(f"Processed one medical report for {self.test_pet.name}", result)

        # Check that send_template_email_async was called once
        self.assertEqual(mock_send_email.delay.call_count, 2)

        # ----- First call: to owner(s)
        call1_args, call1_kwargs = mock_send_email.delay.call_args_list[0]
        self.assertIn(self.test_owner.email, call1_kwargs['to_email'])
        self.assertIn(self.test_pet.name, call1_kwargs['subject'])
        self.assertEqual(call1_kwargs['template_name'], 'emails/medical_report_email.html')

        owner_context = call1_kwargs['context']
        self.assertEqual(owner_context['pet_name'], self.test_pet.name)
        self.assertEqual(owner_context['doctor'], self.test_exam.doctor)
        self.assertEqual(owner_context['clinic_name'], self.test_clinic.clinic.name)
        self.assertEqual(owner_context['reason_for_visit'], self.test_exam.reason_for_visit)
        self.assertEqual(owner_context['diagnosis'], self.test_exam.diagnosis)
        self.assertEqual(owner_context['follow_up'], _('No'))
        self.assertEqual(owner_context['lang'], 'bg')

        # ----- Second call: to clinic
        call2_args, call2_kwargs = mock_send_email.delay.call_args_list[1]
        self.assertEqual(call2_kwargs['to_email'], self.test_clinic.email)
        self.assertIn(self.test_pet.name, call2_kwargs['subject'])
        self.assertEqual(call2_kwargs['template_name'], 'emails/medical_report_email.html')

        clinic_context = call2_kwargs['context']
        self.assertEqual(clinic_context['pet_name'], self.test_pet.name)
        self.assertEqual(clinic_context['doctor'], self.test_exam.doctor)
        self.assertEqual(clinic_context['clinic_name'], self.test_clinic.clinic.name)
        self.assertEqual(clinic_context['follow_up'], _('No'))
        self.assertEqual(clinic_context['lang'], 'bg')

    def test_run_task_manually(self):
        """Test running the task manually (for demonstration purposes)."""
        # This test actually runs the task without mocking
        # It's useful for manual testing but might be skipped in automated tests
        result = send_medical_record_email(self.test_exam, 'bg')
        self.assertIn("Processed", result)

        # Print the result for manual verification
        print(f"\nTask result: {result}")
