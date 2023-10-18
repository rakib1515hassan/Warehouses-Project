from django.urls import path
from .views import *

app_name = 'core'

urlpatterns = [
    path("", HomeView, name="index"),
    path("2/", HomeView2.as_view(), name="index2"),
    path("account_request/", account_request, name="account_request"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("warehouse/", WareHouseList.as_view(),name="warehouse"),
    path("warehouse/<int:pk>/", WareHouseDetails.as_view(),name="warehouse_details"),
    path("mywarehouse/", MyWareHouseList.as_view(),name="mywarehouse"),
    path("warehouse_create/", WarehouseCreateView.as_view(),name="warehouse_create"),
    path('warehouse_update/<int:pk>/', WarehouseUpdateView.as_view(), name='warehouse_update'),
    path('warehouse_delete/<int:w_id>/', WarehouseDeleteView, name='warehouse_delete'),
    path("booking/<int:id>/", create_booking, name="create_booking"),
    path("booking-status/", BookingStatusChange, name="update_booking"),
    path("booking-owner-rating/", BookingOwnerRating, name="owner_rating"),
    path('download-invoice/<int:id>/<str:mode>/', download_invoice, name='download-invoice')
]
