"""trash URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include

from apps.user_profile import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.IndexView.as_view(), name='index'),
    path('', include('apps.user_profile.urls', namespace='user')),
    path('', include('apps.musorka.urls', namespace='musorka')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# # -*- coding: utf-8 -*-
# from django.conf.urls import include, url
# from django.contrib import admin
# from django.conf.urls.i18n import i18n_patterns
# from .views import home, home_files
#
# urlpatterns = [
#     url(r'^(?P<filename>(robots.txt)|(humans.txt))$',
#         home_files, name='home-files'),
# ]
#
# urlpatterns += i18n_patterns(
#     url(r'^$', home, name='home'),
#     url(r'^admin/', include(admin.site.urls)),
# )