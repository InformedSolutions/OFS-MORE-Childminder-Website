from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from application.forms import YourLocationForm


def your_location(request):
    """
    function to handle GET and POST request to the new public beta splitting page
    """

    if request.method == 'GET':
        form = YourLocationForm()
        varaibles = {
            'form': form
        }
        return render(request, 'your-location.html', varaibles)

    if request.method == 'POST':
        form = YourLocationForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['your_location'] == 'True':
                return HttpResponseRedirect(reverse('Account-Selection'))
            else:
                return redirect("https://online.ofsted.gov.uk/onlineofsted/Ofsted_Online.ofml")
        else:
            varaibles = {
                'form': form,
            }
            return render(request, 'your-location.html', varaibles)
