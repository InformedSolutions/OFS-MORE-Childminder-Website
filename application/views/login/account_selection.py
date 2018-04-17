from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from ...forms import AccountSelection


def account_selection(request):
    if request.method == 'GET':
        form = AccountSelection()
        return render(request,'account-selection.html',{'form':form})
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
