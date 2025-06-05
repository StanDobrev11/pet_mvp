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
from django.views.i18n import JavaScriptCatalog
from django.contrib.sitemaps.views import sitemap
from pet_mvp.common.sitemaps import StaticViewSitemap

urlpatterns = [
    # For the set_language view
    path('i18n/', include('django.conf.urls.i18n')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('', include('pet_mvp.common.urls')),
    path('access_codes/', include('pet_mvp.access_codes.urls')),
    path('accounts/', include('pet_mvp.accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('pet_mvp.api.urls')),
    path('pets/', include("pet_mvp.pets.urls")),
    path('records/',
         include([
             path('', include("pet_mvp.records.urls")),
             path('',
                  include("pet_mvp.drugs.urls")
                  )
         ])),
]

sitemaps = {
    'static': StaticViewSitemap,
}
from django.contrib.auth.decorators import login_not_required
urlpatterns += [
    path('sitemap.xml', login_not_required(sitemap), {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

