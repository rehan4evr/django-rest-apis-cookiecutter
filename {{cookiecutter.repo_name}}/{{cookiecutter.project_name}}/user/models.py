from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
    
{% if cookiecutter.api == "y" or cookiecutter.api == "Y" %}
from rest_framework_jwt.utils import jwt_payload_handler
{% endif %}

class AbstractTime(models.Model):
    created_at = models.DateTimeField("Created Date", auto_now_add=True)
    updated_at = models.DateTimeField("Updated Date", auto_now=True)

    class Meta:
        abstract = True

class Country(models.Model):
    code = models.CharField('Code', max_length=256,)
    name = models.CharField('Country Name', max_length=256,)

class MyUserMangement(BaseUserManager):
    def create_user(self, email, username, phone, password):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an Email Address')
        if not email:
            raise ValueError('Users must have an Email Address')

        user = self.model(
            email=self.normalize_email(email),
            phone=phone,
            username=username,
            is_active=False,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, phone, password):
        user = self.model(
            email=email,
            phone=phone,
            username=username
        )
        user.set_password(password)
        user.is_superuser = True
        user.user_type = "Super Admin"
        user.is_active = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class MyUser(AbstractBaseUser, AbstractTime):
     code = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, related_name='code')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    first_name = models.CharField(_('First name'), max_length=50, blank=True)
    last_name = models.CharField(_('Last name'), max_length=50, blank=True)
    email = models.EmailField(_('Email address'), null=True, unique=True, blank=True,error_messages={
                              'unique': "This email id is already registered."})
    mobile = models.CharField('Mobile Number', max_length=256, null=True, unique=True, blank=True,
                                error_messages={'unique': "This mobile id is already registered."})
    image = models.FileField(upload_to='profile/%Y-%M-%d/', null=True, blank=True)
    otp = models.CharField('OTP', max_length=4, blank=True, null=True)
    is_staff = models.BooleanField(_('staff status'), default=False,help_text=_('Designates whether the user can log into this admin site.'), )
    is_active = models.BooleanField(_('active'), default=False, help_text=_('Designates whether this user should be treated as active.'), )
    is_otp_verify = models.BooleanField("OTP Verify", default=False)
    is_superuser = models.BooleanField("Super User", default=False)

    objects = MyUserMangement()
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name','mobile']

    class Meta:
        verbose_name = _('MyUser')
        verbose_name_plural = _('MyUser')
        ordering = ['-pk']

    def __str__(self):
        return self.email

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = "{} {}".format(self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name.strip()
    
    def otp_creation(self):
        '''docstring'''
        totp = pyotp.TOTP("JBSWY3DPEHPK3PXP", digits=4)
        otp = totp.now()
        self.otp = otp
        self.save()
        return otp

    {% if cookiecutter.api == "y" or cookiecutter.api == "Y" %}
    def create_jwt(self):
        """Function for creating JWT for Authentication Purpose"""
        payload = jwt_payload_handler(self)
        token = jwt.encode(payload, settings.SECRET_KEY)
        auth_token = token.decode('unicode_escape')
        return auth_token
    {% endif %}
