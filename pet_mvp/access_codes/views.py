# from django.shortcuts import redirect
# from django.urls import reverse
# from django.views import generic as views
# from django.core.signing import Signer
# from django.contrib.auth import get_user_model
# from django.utils.translation import gettext as _
# from django.contrib import messages
# from datetime import timedelta
# from pet_mvp.access_codes.models import QRShareToken
# from django.utils import timezone
#
# UserModel = get_user_model()
# signer = Signer()
#
#
# # Create your views here.
# class AccessTokenHandlerView(views.View):
#     def get(self, request, token):
#         user = request.user
#
#
#         share_token = QRShareToken.objects.get(token=token)
#
#
#         try:
#             owner_token = PetShareToken.objects.get(token=token)
#             if not owner_token.is_valid():
#                 raise ValueError("Invalid or expired owner token")
#
#             if not user.is_owner:
#                 messages.error(request, _("Only pet owners can use this link."))
#                 return redirect('dashboard')
#
#             # Grant co-ownership
#             pet = owner_token.pet
#             pet.owners.add(user)
#             owner_token.used = True
#             owner_token.save()
#
#             messages.success(request, _("You now have access to %(pet_name)s's profile.") % {"pet_name": pet.name})
#             return redirect('pet-details', pk=pet.pk)
#
#         except (PetShareToken.DoesNotExist, ValueError):
#             pass  # Try vet token next
#
#         # Try vet token
#         try:
#             vet_token = VetAccessToken.objects.get(token=token)
#             if not vet_token.is_valid():
#                 raise ValueError("Invalid or expired vet token")
#
#             if user.is_owner:
#                 return HttpResponseForbidden("Owners cannot use vet access links.")
#
#             VetPetAccess.objects.update_or_create(
#                 vet=user,
#                 pet=vet_token.pet,
#                 defaults={
#                     'granted_at': timezone.now(),
#                     'expires_at': timezone.now() + timedelta(minutes=10),
#                     'granted_by': 'qr'
#                 }
#             )
#
#             vet_token.used = True
#             vet_token.save()
#
#             return redirect(f"{reverse('exam-add')}?source=pet&id={vet_token.pet.pk}")
#
#         except (VetAccessToken.DoesNotExist, ValueError):
#             messages.error(request, _("Invalid or expired token."))
#             return redirect('dashboard')