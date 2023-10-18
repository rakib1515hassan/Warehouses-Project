from django.contrib import admin

from core.models import Accessibility, Availability, Booking, Equipment, Flexible_hours, Insurance, Invoice, Order_taking_time, Payment, Product, Rating, Security, Services_Offered, Start_Date, Storage_space_type, Storage_temperature, Warehouse, Warehouse_Classification, Warehouse_type, WarehousePhoto, Workforce, Contact


from simple_history.admin import SimpleHistoryAdmin


@admin.register(Warehouse)
class Warehouse(SimpleHistoryAdmin):
    ordering = ('-created_at',)
    list_display = ['created_at', 'name', 'owner', 'location']
    search_fields = ['name', 'location']
    date_hierarchy = 'created_at'

admin.site.register(WarehousePhoto)
admin.site.register(Booking)
admin.site.register(Invoice)
admin.site.register(Rating)
admin.site.register(Equipment)
admin.site.register(Security)
admin.site.register(Storage_space_type)
admin.site.register(Availability)
admin.site.register(Accessibility)
admin.site.register(Warehouse_type)
admin.site.register(Storage_temperature)
admin.site.register(Workforce)
admin.site.register(Warehouse_Classification)
admin.site.register(Services_Offered)
admin.site.register(Order_taking_time)
admin.site.register(Flexible_hours)
admin.site.register(Insurance)
admin.site.register(Product)
admin.site.register(Start_Date)
admin.site.register(Payment)
admin.site.register(Contact)
