from django.contrib.auth.models import User

class EmailAuthBackend(object):
    # authenticate using e-mail account
    def authenticate(self,request, username=None, password=None):
        try:
            user = User.objects.get(email=username)  # use email in place of username
            if user.check_password(password):
                return user
            return None
        except User.DoesNotExist:
            return None
        
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None