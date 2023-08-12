from django.shortcuts import render

# Create your views here.


def consumer_home(request):
    context = {}
    return render(request, "consumer_services/base.html", context)