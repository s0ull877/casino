from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Auction
from .forms import AuctionCreateForm

def auctions_view(request):

    auctions = [auction.display_json() for auction in Auction.objects.filter(active=True).exclude(owner=None)]
    diamond_auction = Auction.objects.get_or_create(
        owner=None,
        max_members=20,
        min_bet=1,
        active=True
    )[0]

    return render(request, 'auctions/auctions2.html', context={'auctions': auctions, 'diamond_auction': diamond_auction, 'form': AuctionCreateForm()})

@login_required
def auction_view(request, group_name):

    try:
        auction = Auction.objects.select_related('owner').prefetch_related('members','bets').get(group_name=group_name)
    except Auction.DoesNotExist:
        raise Http404()

    return render(request, 'auctions/auction_game.html', context={'auction': auction})


@login_required
def diamond_auction_view(request):

    try:
        auction = Auction.objects.prefetch_related('members','bets').filter(owner=None, active=True).first()
    except Auction.DoesNotExist:
        raise Http404()

    return render(request, 'auctions/auction_game.html', context={'auction': auction})


def auction_over_view(request, group_name):

    try:
        auction = Auction.objects.prefetch_related('bets').get(group_name=group_name)
    except Auction.DoesNotExist:
        auction = None

    return render(request, 'auctions/auction_over.html', context={'auction': auction})


@login_required
def auction_create_view(request):

    data = {
        'owner': request.user,
        'max_members': request.POST.get('max_members'),
        'min_bet': request.POST.get('min_bet'),
    }

    form = AuctionCreateForm(data)

    if form.is_valid():

        auction: Auction = form.save()

        return redirect(to='auctions:auction', group_name=auction.group_name)

    return HttpResponseRedirect(redirect_to=reverse('auctions:index'))


