import re
from django.contrib.auth import get_user_model

User = get_user_model()

def handle_tags(text, person=None, comment=None):
    tagged_usernames = re.findall(r'@(\w+)', text)

    for username in tagged_usernames:
        try:
            tagged_usernames = User.objects.get(username=username)
            print(f"{tagged_usernames.username} was mentioned")

        except User.DoesNotExist:
            continue

    return tagged_usernames