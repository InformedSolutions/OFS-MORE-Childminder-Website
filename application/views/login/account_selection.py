from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from ...forms import AccountSelection


def account_selection(request):
    """
    Function for redirecting user to either the login page or new account page based on their
    response to whether or not they are returning to an application
    :param request: inbound HTTP request
    :return: redirect to account sign up or return page
    """
    if request.method == 'GET':
        form = AccountSelection()
        return render(request,'account-selection.html', {'form':form})
    if request.method == 'POST':
        form = AccountSelection(request.POST)
        if form.is_valid():
            acc_selection = form.cleaned_data['acc_selection']
            if 'new' in acc_selection:
                # Start new application
                return HttpResponseRedirect(reverse('New-Email'))
            if 'existing' in acc_selection:
                # Sign in
                return HttpResponseRedirect(reverse('Existing-Email'))
        return render(request, 'account-selection.html', {'form': form})
