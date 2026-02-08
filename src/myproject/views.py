from django.http import HttpResponse
from django.shortcuts import render

def home_page_view(request, *args, **kwargs):
    # return HttpResponse("<h1>Working</h1>")
    my_title = "Home page"
    html_template = "home.html"
    mycontext = {
        "page_title": my_title
    }
    return render(request, html_template, mycontext)