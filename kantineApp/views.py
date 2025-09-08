from django.contrib.auth import login as _login
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token
from django.http import JsonResponse


@csrf_exempt
def login(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    m = authenticate(username=username, password=password)
    if m and m.is_active:
        # request.session.set_expiry(86400)  # sets the exp. value of the session
        _login(request, m)  # the user is now logged in
        return HttpResponse("You're logged in.")
    else:
        return HttpResponse("Your username and password didn't match.")


def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})


# @login_required
def is_loggedin(request):
    if request.user.is_authenticated:
        return HttpResponse("ok")
    else:
        return HttpResponse("Not authenticated", 403)
