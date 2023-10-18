from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password

from account.models import WarehouseUser


class EmailAuthenticationForm(AuthenticationForm):
    username = None
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'autofocus': True}),
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields.pop('username')
        self.fields.move_to_end('password')

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            # Authenticate using email and password
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'email': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class RegistrationForm(forms.ModelForm):
    Business = 'BUSINESS'
    WarehouseOwner = 'WAREHOUSE_OWNER'

    AccountType = (
        (Business, "Business"),
        (WarehouseOwner, "Warehouse_owner"),
    )

    first_name = forms.CharField(label='First Name', widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(label='Last Name', widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'placeholder': 'Email', 'autofocus': True}))
    account_type = forms.ChoiceField(label='Account Type', choices=AccountType, widget=forms.Select(attrs={'class': 'form-select'}),)
    company_name = forms.CharField(label='Company Name', widget=forms.TextInput(attrs={'placeholder': 'Company Name'}),required=False)
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
                               validators=[validate_password])
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    class Meta:
        model = WarehouseUser
        fields = ["first_name", "last_name", "username", "email", "account_type", "company_name", "password", "confirm_password"]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.ChoiceField):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'The passwords do not match.')

        return cleaned_data
