"""morebeta URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib import admin
from application import views

urlpatterns = [
    url(r'^$',views.StartPageView, name='start-page.html'),
    url(r'^task-list/', views.LogInView, name='morebeta'),
    url(r'^childcare/', views.TypeOfChildcareView, name='Type-Of-Childcare-View'),
    url(r'^contact-email/', views.ContactEmailView, name='Contact-Email-View'),
    url(r'^personal-details/', views.PersonalDetailsView, name='Personal-Details-View'),
    url(r'^dbs-check/', views.DBSCheckView, name='DBS-Check-View'),
    url(r'^first-aid/', views.FirstAidTrainingView, name='First-Aid-Training-View'),
    url(r'^other-people/', TemplateView.as_view(template_name='other-people.html'), name='morebeta'),
    url(r'^declaration/', TemplateView.as_view(template_name='declaration.html'), name='morebeta'),
    url(r'^admin/', admin.site.urls),
    ]
    
