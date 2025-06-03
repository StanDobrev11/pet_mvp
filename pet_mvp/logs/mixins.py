from pet_mvp.logs.models import PetAccessLog


class PetAccessLoggingMixin:
    access_log_method = 'owner'  # override per view if needed

    def log_pet_access_once_per_session(self, request, pet):
        session_key = f'logged_pet_{pet.id}_method_{self.access_log_method}'

        if request.session.get(session_key):
            return  # Already logged this pet with this method in this session

        user = request.user if request.user.is_authenticated else None

        PetAccessLog.objects.create(
            pet=pet,
            accessed_by=user,
            method=self.access_log_method,
            ip_address=self.get_client_ip(request),
        )

        request.session[session_key] = True  # mark as logged


    def get_client_ip(self, request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0]
        return request.META.get('REMOTE_ADDR')