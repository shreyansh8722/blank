
from django.contrib.auth.forms import UserCreationForm
from users.models import NewUser

class CreateUserForm(UserCreationForm):
    class Meta:
        model = NewUser
        fields = ['name', 'mobile_no','user_type', 'password1','password2']