from django.shortcuts import render

from application.views.declaration import declaration_summary


def base_print_handler(request, page):

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        order_code = request.GET["orderCode"]
        variables = {'app_id': application_id_local,
                     'order_code': order_code,
                     'print_class': 'visually-hidden'}
        if page == 'master-summary':
            variables.update(declaration_summary(request, print_mode=True))

        return render(request, str(page + '.html'), variables)

