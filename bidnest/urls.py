"""
URL configuration for BidNest project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from properties.views import home, contact

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('contact/', contact, name='contact'),
    path('privacy/', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    path('terms/', TemplateView.as_view(template_name='terms.html'), name='terms'),
    path('accounts/', include('accounts.urls')),
    path('properties/', include('properties.urls')),
    path('bidding/', include('bidding.urls')),
    path('messages/', include('messaging.urls')),
    path('payments/', include('payments.urls')),
    path('contracts/', include('contracts.urls')),
    path('notifications/', include('notifications.urls')),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = "BidNest Administration"
admin.site.site_title = "BidNest Admin"
admin.site.index_title = "Welcome to BidNest Admin Portal"
