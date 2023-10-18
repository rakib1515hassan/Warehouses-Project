from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from warehouses1201 import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('', include('chat.urls', namespace='chat')),
    path('account/', include('account.urls', namespace='account')),
    path('', include('social_django.urls', namespace='social')),
    path('faq/', include('faq.urls', namespace='faq')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT,show_indexes=True)
