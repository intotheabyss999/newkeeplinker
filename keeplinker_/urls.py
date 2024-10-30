"""
URL configuration for keeplinker_ project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Main app URLs
    path('', include('main.urls', namespace='main')),
    
    # Auth app URLs (your custom URLs)
    path('auth/', include(('auth_app.urls', 'auth_app'), namespace='auth_app')),  
    
    # Include allauth URLs separately (this is crucial for social login to work)
    path('accounts/', include('allauth.urls')),  
    
    # Collections app URLs
    path('collections/', include(('collections_app.urls', 'collections_app'), namespace='collections_app')),
] 


