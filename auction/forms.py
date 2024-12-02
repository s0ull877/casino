from django import forms

from .models import Auction

class AuctionCreateForm(forms.ModelForm):

    class Meta:
        model= Auction
        fields = ['owner', 'max_members', 'min_bet']
