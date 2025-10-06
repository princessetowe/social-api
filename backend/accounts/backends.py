from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from phonenumber_field.phonenumber import to_python

User = get_user_model()

class BackendAuth(ModelBackend):

    def authenticate(self, request, username = None, password = None, **kwargs):
        if username is None or password is None:
            return None
        
        try:
            parsed_phone = to_python(username)
            if parsed_phone and parsed_phone.is_valid():
                user = User.objects.get(phone_number=parsed_phone)
            else:
                user = User.objects.get(
                    Q(username__iexact=username) | Q(email__iexact=username)
                )

        except User.DoesNotExist:
            return None
        
        if user.check_password(password):
            return user
        
        return None