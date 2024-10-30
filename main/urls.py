from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'main'  # This line defines the namespace

urlpatterns = [
  path('', views.index, name='index'),
  path('signin/', views.signin, name='signin'),  # URL for SignIn page
  path('signup/', views.signup, name='signup'),  # URL for SignUp page
  # path('auth/', include(('auth_app.urls', 'auth_app'), namespace='auth_app')),
  # path('', include('main.urls')),
  # path('auth/', include('django.contrib.auth.urls')),
  path('auth/', include('auth_app.urls', namespace='auth_app')),
  # path('collections/', include('django.contrib.collections.urls')),
  path('terms/', views.terms, name='terms'),
  path('privacy/', views.privacy, name='privacy'),
  path('about/', views.about, name='about'),
  path('accounts/', include('allauth.urls')),  # Add allauth URLs
  path('dashboard/', views.dashboard, name='dashboard'),
  
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

