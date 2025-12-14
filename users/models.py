from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class CustomAccountManager(BaseUserManager):

    def create_superuser(self, name, mobile_no, password, **other_fields):
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('is_staff', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(name, mobile_no, password, **other_fields)

    def create_user(self, name, mobile_no, password, **other_fields):

        other_fields.setdefault('is_active', True)
        other_fields.setdefault('is_staff', True)
        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')

        user = self.model(mobile_no=mobile_no, name=name, **other_fields)
        user.set_password(password)
        user.save()
        return user


AUTH_PROVIDERS = {'facebook': 'facebook', 'google': 'google',
                  'twitter': 'twitter'}

USER_TYPE = (
    ("Teacher", "Teacher"),
    ("School", "School"),
    ("Admin", "Admin"),
)


class NewUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=250, blank=True, null=True)
    mobile_no = models.CharField(max_length=13, null=True, unique=True)
    alt_mobile_no = models.CharField(max_length=13, null=True, blank=True)
    profile_pic = models.ImageField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_mobile_no_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    joining_date = models.DateTimeField(default=timezone.now)
    user_type = models.CharField(max_length=15, choices=USER_TYPE, default='User', blank=True)
    is_active = models.BooleanField(default=True)
    is_mobile_no_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    temp_data = models.CharField(max_length=50, blank=True, null=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'mobile_no'
    REQUIRED_FIELDS = ['name', 'password']

    def __str__(self):
        return self.mobile_no

    class Meta:
        verbose_name_plural = "Users"


class OtpHistory(models.Model):

    user = models.ForeignKey(NewUser, on_delete=models.SET_NULL, null=True,blank=True)
    otp = models.CharField(max_length=50, null=True,blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    otp_session = models.DecimalField(max_digits=1, decimal_places=0, default=0,null=True,blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = "Otp History"

class UserLog(models.Model):

    user = models.ForeignKey(NewUser, on_delete=models.SET_NULL, null=True,blank=True)
    action = models.CharField(max_length=50, null=True,blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
   
    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = "Users Log"