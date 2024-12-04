from django.http import Http404
from django.shortcuts import redirect, render, HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.urls import reverse
from ballance.models import BallanceTransaction
from django.db.models import Sum
from django.contrib.auth.decorators import login_required

from .models import User

def login_view(request):

    if request.method == 'POST':

        user = authenticate(
            username=request.POST.get('user_id'),
            password=request.POST.get('password'),
        )

        if user is None:
            request.session['password_invalid'] = True
            return redirect(request.META['HTTP_REFERER'])
        
        else:

            request.session['password_invalid'] = False
            login(request=request, user=user)
            return HttpResponseRedirect(reverse('users:games'))
    
    if not request.GET.get('user_id'):
        raise Http404()
    
    user_id= request.GET.get('user_id')
    
    return render(request, 'users/login.html', context={'user_id': user_id})


@login_required
def profile_view(request):

    game_history = BallanceTransaction.objects.filter(ballance__user=request.user).exclude(title__startswith="@").order_by('-time')

    ballance_history = BallanceTransaction.objects.filter(ballance__user=request.user, title__startswith="@").order_by('-time')

    return render(request=request, template_name='users/profile.html', context={'game_history': game_history, 'ballance_history':ballance_history})


@login_required
def games_view(request):
    return render(request, 'users/index.html')


@login_required
def top_users_view(request):
    context = {}

    top_users = User.objects.select_related('wallet').all()
    context['count'] = top_users.count()
    context['top_users'] = sorted(top_users, key=lambda user: user.total_bet, reverse=True)[:100]

    return render(request=request, template_name='users/top_players.html', context=context)


@login_required
def settings_view(request):

    return render(request=request, template_name='users/settings.html')