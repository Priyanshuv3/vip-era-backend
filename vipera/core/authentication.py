from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from user_management.models import UserAccount

class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserAccount.objects.get(Q(email=username) | Q(phone_number=username))
            if user.check_password(password):
                return user
        except UserAccount.DoesNotExist:
            return None
