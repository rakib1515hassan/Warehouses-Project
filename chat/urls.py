
from django.urls import path, include
from chat import views
app_name = "chat"
urlpatterns = [
    path('account/chat/', views.MessageView, name="message"),
    path('account/chat/send_message/', views.SendMessage, name="send_message"),
    path('account/chat/get_messages/', views.get_messages, name='get_message')
]
