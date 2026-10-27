from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from accounts.views import register
from detector.views import custom_logout


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('detector.urls')),
    path('marketplace/', include('marketplace.urls')), 
    path('community/', include('community.urls')),
    path('weather/', include('analytics.urls')),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('register/', register, name='register'),
    path('logout/', custom_logout, name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)