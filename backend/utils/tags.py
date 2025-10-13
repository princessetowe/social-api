import re
from django.contrib.auth import get_user_model

User = get_user_model()

def handle_tags(text, person=None, comment=None):
    tagged_usernames = re.findall(r'@(\w+)', text)
    return User.objects.filter(username__in=tagged_usernames)