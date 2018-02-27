from django.contrib.sites.models import Site
from django.conf import settings

def site_processor(request):
    return { 'siteInfo': Site.objects.get_current(), 'DEMO': settings.DEMO, 'CENTRAL_MEDIA_URL': settings.CENTRAL_MEDIA_URL }
