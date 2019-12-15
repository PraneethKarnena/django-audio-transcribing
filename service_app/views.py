from django.shortcuts import render


def home_view(request):
    """
    Added Home page
    """
    return render(request, 'service/home.html')