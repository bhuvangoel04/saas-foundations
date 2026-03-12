from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import get_user_model
# Create your views here.
User = get_user_model()

@login_required
def profile_view(request,username=None, *args, **kwargs):
    user = request.user # logged in user
    # profile_user_obj = User.objects.get(username=username)
    profile_user_obj = get_object_or_404(User, username=username) # username is username of user whose profile the logged in user is viewing (entered in the url)
    is_me = profile_user_obj == user
    return HttpResponse(f"Hello There {username} - {profile_user_obj.id} - {user.id} -{is_me}")