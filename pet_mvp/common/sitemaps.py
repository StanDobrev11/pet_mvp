from django.conf import settings
from types import SimpleNamespace
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'monthly'

    def items(self):
        return [
            'index',
            'about',
            'login',
            'register',
            'clinic-login',
            'password-entry',
            'clinic-register',
            'forgot-password',
        ]

    def location(self, item):
        return reverse(item)

    def get_urls(self, site=None, **kwargs):
        domain = settings.BASE_URL.replace("http://", "").replace("https://", "").rstrip("/")
        site = SimpleNamespace(domain=domain, name="My Pet Passport")
        return super().get_urls(site=site, **kwargs)