from django.http import Http404
from django.shortcuts import redirect, render, HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.urls import reverse
from ballance.models import BallanceTransaction
from django.db.models import Sum

from .models import User

def login_view(request):

    if request.method == 'POST':

        user = authenticate(
            username=request.POST.get('user_id'),
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


def profile_view(request):

    game_history = BallanceTransaction.objects.filter(ballance__user=request.user).exclude(title__startswith="@").order_by('-time')

    ballance_history = BallanceTransaction.objects.filter(ballance__user=request.user, title__startswith="@").order_by('-time')

    return render(request=request, template_name='users/profile.html', context={'game_history': game_history, 'ballance_history':ballance_history})


def games_view(request):
    return render(request, 'users/index.html')

def top_users_view(request):

    top_users = User.objects.select_related('wallet').all()
    top_users = list(filter(lambda user: user.total_bet, top_users))[::-1]

    return render(request=request, template_name='users/top_players.html', context={'top_users': top_users[:10]})


