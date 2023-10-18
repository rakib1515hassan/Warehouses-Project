from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

Business = 'BUSINESS'
WarehouseOwner = 'WAREHOUSE_OWNER'
Admin = 'ADMIN'

AccountType = (
    (Business, "Business"),
    (WarehouseOwner, "Warehouse_owner"),
    (Admin, "Admin")
)


class WarehouseUser(AbstractUser):
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=20, blank=True)
    account_type = models.CharField(max_length=20, choices=AccountType, default=Business)
    is_email_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=10, null=True, blank=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)

    def email_exists(email):
        if WarehouseUser.objects.filter(email=email).exists():
            return True

        return False


class AccountTypeChangeRequest(models.Model):
    user = models.ForeignKey(WarehouseUser, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} request for warehouse owner account"
