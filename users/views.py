from django.http import Http404
from django.shortcuts import redirect, render, HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse

def login_view(request):


    if request.method == 'POST':

        user = authenticate(
            user_id=request.POST.get('user_id'),
            password=request.POST.get('password'),
        )

        if user is None:
            return redirect(request.META['HTTP_REFERER'])
        
        else:

            login(request=request, user=user)
            return HttpResponseRedirect(reverse('users:games'))
    
    if not request.GET.get('user_id'):
        raise Http404()
    
    return render(request, 'users/login.html')


def games_view(request):
    return render(request, 'users/games.html')


