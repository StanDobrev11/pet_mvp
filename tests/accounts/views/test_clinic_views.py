from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from caller import set_site_domain
from pet_mvp.pets.models import Pet

UserModel = get_user_model()


class ApproveTempClinicViewTests(TestCase):
    def setUp(self):
        self.owner = UserModel.objects.create_owner(
            email='owner@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Owner',
            phone_number='0887654321',
            city='Sofia',
            country='Bulgaria'
        )
        self.clinic = UserModel.objects.create_clinic(
            email='clinic@example.com',
            password='testpass123',
            clinic_name='Clinic',
            clinic_address='Addr',
            phone_number='0887654322',
            city='Sofia',
            country='Bulgaria',
            is_active=False
        )
        self.pet = Pet.objects.create(
            name='Pet',
            species='Dog',
            breed='Breed',
            color='Tan',
            features='',
            date_of_birth='2020-01-01',
            sex='male',
            current_weight='10',
            passport_number='BG01VP111000'
        )
        self.pet.owners.add(self.owner)

    def test_missing_parameters(self):
        response = self.client.get(reverse('approve-temp-clinic'))
        self.assertRedirects(response, reverse('index'),
                             fetch_redirect_response=False)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Invalid approval request' in str(m)
                        for m in messages))

    def test_activation_success(self):
        url = reverse('approve-temp-clinic') + \
            f'?clinic_id={self.clinic.id}&pet_id={self.pet.id}'
        response = self.client.get(url, follow=True)
        self.clinic.refresh_from_db()
        self.assertTrue(self.clinic.is_active)
        self.assertRedirects(response, reverse('index'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('has been activated' in str(m) for m in messages))

    def test_already_active_info(self):
        self.clinic.is_active = True
        self.clinic.save()
        url = reverse('approve-temp-clinic') + \
            f'?clinic_id={self.clinic.id}&pet_id={self.pet.id}'
        response = self.client.get(url, follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertRedirects(response, reverse('index'))
        self.assertTrue(any('already activated' in str(m) for m in messages))


class CustomPasswordResetConfirmViewTests(TestCase):
    def setUp(self):
        self.owner = UserModel.objects.create_owner(
            email='owner2@example.com',
            password='testpass123',
            first_name='Owner',
            last_name='Two',
            phone_number='0887654324',
            city='Sofia',
            country='Bulgaria'
        )
        self.clinic = UserModel.objects.create_clinic(
            email='clinic2@example.com',
            password='testpass123',
            clinic_name='Clinic2',
            clinic_address='Addr2',
            phone_number='0887654323',
            city='Sofia',
            country='Bulgaria',
            is_active=False,
            is_approved=True,
        )

    def _reset_url(self, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        return reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
    
    def _get_reset_url_with_token(self, user):
        """Get the reset URL and follow Django's password reset flow to get the token in the session"""
        url = self._reset_url(user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        return response.url

    def test_clinic_activation_and_redirect(self):
        # Get the password reset URL with token
        url = self._get_reset_url_with_token(self.clinic)
        
        # Get the password reset form
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Submit the new password
        response = self.client.post(url, {
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        }, follow=True)

        self.clinic.refresh_from_db()
        self.assertTrue(self.clinic.is_active)
        self.assertRedirects(response, reverse('clinic-login'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Password set successfully' in str(m) for m in messages))

    def test_owner_redirect(self):
        # Get the password reset URL with token
        url = self._get_reset_url_with_token(self.owner)
        
        # Get the password reset form
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Submit the new password
        response = self.client.post(url, {
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        }, follow=True)

        self.assertRedirects(response, reverse('login'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Password set successfully' in str(m) for m in messages))
