"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import include, path
from django.conf.urls import url
from django.views.generic import TemplateView

from rest_framework import routers
from rest_framework.schemas import get_schema_view

from machineconfig.views import tftp
from machineconfig.views import tftp_default
from machineconfig.views import kickstart

from machineconfig.api_views import lcogtinstruments
from machineconfig.api_views import tools_ping
from machineconfig.api_views import tools_host
from machineconfig.api_views import tools_dig
from machineconfig.api_views import tools_traceroute

from machineconfig.viewsets import SiteViewSet
from machineconfig.viewsets import NetworkDeviceViewSet
from machineconfig.viewsets import UnrecognizedPXEDeviceViewSet
from machineconfig.viewsets import BootHistoryViewSet
from machineconfig.viewsets import BuildHistoryViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'site', SiteViewSet)
router.register(r'networkdevice', NetworkDeviceViewSet)
router.register(r'unrecognized-pxe-device', UnrecognizedPXEDeviceViewSet)
router.register(r'boot-history', BootHistoryViewSet)
router.register(r'build-history', BuildHistoryViewSet)

# Common MAC address pattern
macaddress = r'(?P<macaddress>([0-9a-f]{2}[\-:]){5}([0-9a-f]{2}))'
sitecode = r'(?P<sitecode>([a-zA-Z]{3}))'

# NOTE:
# This software requires NGINX to lowercase these URLs before the Django URL
# router sees them. The various PXE firmware is very low quality, and cannot
# handle redirects. Django removed support for case insensitive URL routing
# in version 2.1, so now we have to implement it ourselves.
urlpatterns = (
    # TFTP and Kickstart automatic file generation by MAC address
    url(r'^tftp/.*default$', tftp_default),
    url(r'^tftp/.*' + macaddress + r'$', tftp, name='tftp'),
    url(r'^ks/.*' + macaddress + r'$', kickstart, name='kickstart'),
    url(r'^kickstart/.*' + macaddress + r'$', kickstart),

    # heath check
    url(r'^healthz/', include('watchman.urls')),

    # Django REST Framework views
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^api/lcogtinstruments/', lcogtinstruments, name='lcogtinstruments'),
    url(r'^api/tools/ping/(?P<target>([^/]+))/', tools_ping, name='tools_ping'),
    url(r'^api/tools/host/(?P<target>([^/]+))/', tools_host, name='tools_host'),
    url(r'^api/tools/dig/(?P<target>([^/]+))/', tools_dig, name='tools_dig'),
    url(r'^api/tools/traceroute/(?P<target>([^/]+))/', tools_traceroute, name='tools_traceroute'),

    # Django REST Framework OpenAPI SchemaView
    # https://www.django-rest-framework.org/api-guide/schemas/
    # https://www.django-rest-framework.org/topics/documenting-your-api/
    path('openapi', get_schema_view(
        title="LCO IT Portal",
        description="API for all things …",
        version="1.0.0"
    ), name='openapi-schema'),
    path('swagger-ui/', TemplateView.as_view(
        template_name='swagger-ui.jinja',
        extra_context={'schema_url':'openapi-schema'}
    ), name='swagger-ui'),
    path('redoc/', TemplateView.as_view(
        template_name='redoc.jinja',
        extra_context={'schema_url':'openapi-schema'}
    ), name='redoc'),
)

# vim: set ts=4 sts=4 sw=4 et:
