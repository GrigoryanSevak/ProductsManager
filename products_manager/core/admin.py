from django.contrib import admin

from django import forms

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from django.contrib.auth import get_user_model

# from .models import SeoForPath

User = get_user_model()

# Register your models here.


class AutoSlugPublishedAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ('published', )


class PublishedAdmin(admin.ModelAdmin):
    list_filter = ('published', )


class AutoSlugAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label=u'Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label=u'Подтверждение пароля', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(u"Пароли не совпадают")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(
        label="Password",
        help_text=
            "Raw passwords are not stored, so there is no way to see this " \
            "user's password, but you can change the password using " \
            "<a href=\"../password/\">this form</a>.", \
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'is_active', 'is_staff', )

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username', 'email', 'is_staff', 'is_active', )
    list_filter = ('is_staff', 'is_active', )
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'first_name', 'last_name', )}),
        ('Разрешения', {'fields': ('is_superuser', 'is_staff', 'is_active', )}),
        ('Доступы', {'fields': ('groups', 'user_permissions', )}),
        ('Другое', {'fields': ('delivery_address', )}),

    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2',  )}
         ),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name', )
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions', )


admin.site.register(User, UserAdmin)
# admin.site.register(SeoForPath)
# admin.site.register(Address)
