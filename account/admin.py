from django.contrib import admin

from account.models import WarehouseUser, AccountTypeChangeRequest

# Register your models here.
admin.site.register(WarehouseUser)
admin.site.register(AccountTypeChangeRequest)