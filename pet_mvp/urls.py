"""
URL configuration for pet_mvp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # For the set_language view
    path('', include('pet_mvp.common.urls')),
    path('access_codes/', include('pet_mvp.access_codes.urls')),
    path('accounts/', include('pet_mvp.accounts.urls')),
    path('admin/', admin.site.urls),
    path('pets/', include("pet_mvp.pets.urls")),
    path('records/',
         include([
             path('', include("pet_mvp.records.urls")),
             path('',
                  include("pet_mvp.drugs.urls")
                  )
         ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
