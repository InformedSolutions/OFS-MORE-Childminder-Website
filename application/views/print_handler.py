import datetime
import json
import re
from uuid import UUID

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from application.views.declaration import declaration_summary


def base_print_handler(request, page):

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        order_code = request.GET["orderCode"]
        variables = {'app_id': application_id_local,
                     'order_code': order_code,
                     'print_class': 'visually-hidden'}
        if page == 'master-summary':
            variables.update(declaration_summary(request, print=True))

        return render(request, str(page + '.html'), variables)

