"""WarLlama URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^', include('Alpaca.urls')) ## Enabling translation
]

## About Multi-Language, quoting: 
## http://stackoverflow.com/questions/10280881/django-site-with-2-languages/26520044#26520044
# Wrap your text with lazytext! import lazytext (as above) and wrap every string 
# with it like so _('text'), you can even go to your other urls.py files and do url 
# translation like so:
#
# >>> url(_(r'^dual_language/$'), landing, name='duallang_landing'), <<<
#
# You can wrap text that you want translated in your other files, such as models.py, 
# views.py etc.. Here is an example model field with translations for label and help_text:
#
# >>> name = models.CharField(_('name'), max_length=255, unique=True, help_text=_("Name of the FAQ Topic")) <<<
#
# Django translation docs are great for this!