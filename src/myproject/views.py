from django.http import HttpResponse
from django.shortcuts import render
from visits.models import PageVisit

def home_page_view(request, *args, **kwargs):
    # return HttpResponse("<h1>Working</h1>")
    path=request.path
    print(path)
    PageVisit.objects.create(path=request.path)
    qs = PageVisit.objects.all() # The all() method returns a QuerySet of all the objects in the database.
    page_qs = PageVisit.objects.filter(path=request.path)
    my_title = "Home page"
    html_template = "home.html"
    try:
        percent = ((page_qs.count()*100)/qs.count())
    except:
        percent = 0
    mycontext = {
        "page_title": my_title,
        "total_page_visits": qs.count(),
        "percent": percent,
        "page_visit_count": page_qs.count(), # counts all the page visit objects created i.e. is no. of page visits
    }
    return render(request, html_template, mycontext)