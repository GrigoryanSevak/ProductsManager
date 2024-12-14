from django.db import models

from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin

from .validators import ASCIIUsernameValidator, UnicodeUsernameValidator
import six

# Create your models here.


class MyUserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager"
    """

    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not username:
            raise ValueError('The username must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    FIZ = 'fiz'
    JUR = 'jur'
    USER_TYPES = (
        (FIZ, u'Физическое лицо'),
        (JUR, u'Юридическое лицо'),

    )
    username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()
    username = models.CharField(
        verbose_name='Номер телефона',
        max_length=30,
        unique=True,
        db_index=True,
        help_text='Обязательное поле. Максимум 30 символов. Только цифры и +',
        validators=[username_validator],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    user_type = models.CharField(choices=USER_TYPES, max_length=3, verbose_name='Тип пользователя', default=FIZ)
    email = models.EmailField(verbose_name='Email', max_length=200)

    first_name = models.CharField(max_length=200, verbose_name='First Name', blank=True)
    last_name = models.CharField(max_length=200, verbose_name='Last Name', blank=True)

    company_name = models.CharField(verbose_name='Полное наименование', max_length=250, blank=True)
    company_inn = models.CharField(verbose_name='ИНН', max_length=12, blank=True)
    company_kpp = models.CharField(verbose_name='КПП', max_length=9, blank=True)
    company_ogrn = models.CharField(verbose_name='ОГРН', max_length=13, blank=True)
    company_address = models.CharField(verbose_name='Юридический адрес', max_length=500, blank=True)
    company_account = models.CharField(verbose_name='Расчетный счет', max_length=20, blank=True)
    company_bank_name = models.CharField(verbose_name='Наименование банка', max_length=500, blank=True)
    company_bank_account = models.CharField(verbose_name='Кор счет банка', max_length=20, blank=True)
    company_bank_bik = models.CharField(verbose_name='БИК банка', max_length=9, blank=True)

    temp_sms = models.CharField(max_length=6, blank=True)

    modified = models.DateTimeField(auto_now=True)
    joined = models.DateTimeField(auto_now_add=True)

    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Designates whether the user can log into this site.',
    )

    is_active = models.BooleanField(
        'active',
        default=False,
        help_text=
            'Designates whether this user should be treated as active. ' \
            'Unselect this instead of deleting accounts.',
    )

    delivery_address = models.TextField(verbose_name='Адрес доставки', blank=True)

    avatar = models.ImageField(upload_to='user_avatars', max_length=500, blank=True)

    USERNAME_FIELD = 'username'

    objects = MyUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

    def get_fav_products_ids(self) -> list:
        result = list()
        for item in self.fav_records_new.all():
            result.append(item.product.pk)
        return list(set(result))

    def user_orders(self):
        return self.orders.all()

    def all_orders_count(self):
        return self.user_orders().count()

    def complete_orders_count(self):
        return self.user_orders().filter(status='complete').count()

    def canceled_orders_count(self):
        return self.user_orders().filter(status='canceled').count()

    def get_full_name(self):
        if self.first_name and self.last_name:
            return '{} {}'.format(self.first_name, self.last_name)
        return self.email

    def get_short_name(self):
        if self.first_name:
            return '{}'.format(self.first_name)
        return self.email
    #
    # def email_user(self, subject, message, from_email=None, **kwargs):
    #     """Send an email to this user."""
    #     send_mail(subject, message, from_email, [self.email], **kwargs)


class Seo(models.Model):
    seo_title = models.CharField(max_length=200, blank=True, verbose_name='SEO title')
    search_description = models.CharField(max_length=250, blank=True, verbose_name='SEO description')

    class Meta:
        abstract = True
