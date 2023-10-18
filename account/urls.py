from django.urls import path
from .views import *

app_name = 'account'

urlpatterns = [
    path('', AccountDetail.as_view(), name='account'),
    path('booking/', Bookings.as_view(), name='bookings'),
    path('space-request/', SpaceRequest.as_view(), name='space_request'),
    path('details/', Details.as_view(), name='details'),
    path('settings/', Settings.as_view(), name='settings'),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path('signup/',user_signup, name="signup"),
    path('signup/validate_field/', validate_field, name='validate_field'),
    path('verify_email/',verify_email, name="verify_email"),
    path('not_verified/',not_verified, name="not_verified"),
    path("complete_profile/", complete_profile, name="complete_profile"),
    path('forget-password', forget_password, name='forget_password'),
    path('reset_password/',reset_password,name='reset_password'),
    path('resetpassword_validate/<uidb64>/<token>/<time64>/', resetpassword_validate, name='resetpassword_validate'),
    path('export-bookings-csv/', export_bookings_csv, name='export_bookings_csv'),
    path('export/', export_view, name='export_view'),
    path('customer_list/', customer_list, name='customer_list'),
    path('customer_request/', customer_request, name='customer_request'),
]
