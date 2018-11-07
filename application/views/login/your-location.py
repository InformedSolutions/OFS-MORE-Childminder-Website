from django.shortcuts import render
from requests import request
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
        form = YourLocationForm()

        if form.is_valid():

            if form.cleaned_data['your_location']:

                # Redirect to BETA service for london New-Email

            else:

                # Redirect to existing service
        else:
            # Form is not valid, return page
            varaibles ={
                'form': form,
            }
            return render(request, 'your-location.html', varaibles)





