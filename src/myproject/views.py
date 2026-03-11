from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from visits.models import PageVisit

def home_page_view(request, *args, **kwargs):
    if request.user.is_authenticated:
        print(request.user.first_name)
    return about_view(request, *args, **kwargs)

def about_view(request, *args, **kwargs):
    # return HttpResponse("<h1>Working</h1>")
    path=request.path
    print(path)
    PageVisit.objects.create(path=request.path)
    qs = PageVisit.objects.all() # The all() method returns a QuerySet of all the objects in the database.
    page_qs = PageVisit.objects.filter(path=request.path)
    my_title = "Home page"
    html_template = "home.html"
    try:
        percent = round((page_qs.count() * 100) / qs.count(), 2)
    except:
        percent = 0
    mycontext = {
        "page_title": my_title,
        "total_page_visits": qs.count(),
        "percent": percent,
        "page_visit_count": page_qs.count(), # counts all the page visit objects created i.e. is no. of page visits
    }
    return render(request, html_template, mycontext)

VALID_CODE = "abc123"

def pw_protected_view(request, *args, **kwargs):
    is_allowed = request.session.get('protected_page_allowed') or 0
    # print(request.session.get('protected_page_allowed'), type)
    if(request.method == "POST"):
        user_pw_sent = request.POST.get("code") or None
        if user_pw_sent == VALID_CODE:
            is_allowed=1
            request.session['protected_page_allowed'] = 1
    if is_allowed:
        return render(request, "protected/view.html", {})
    return render(request, "protected/entry.html", {})

@login_required
def user_only_view(request, *args, **kwargs):
    # print(request.user.is_staff)
    return render(request, "protected/user-only.html", {})