from django import forms

from .models import Auction

class AuctionCreateForm(forms.ModelForm):

    class Meta:
        model= Auction
        fields = ['owner', 'max_members', 'min_bet']
        widgets = {
            'max_members' : forms.NumberInput(attrs={
                "type": 'range',
                "min":10, 
                "max":50,
                "value":10,
                "step":1
            }),
            'min_bet' : forms.NumberInput(attrs={
                "type": 'range',
                "min":1, 
                "max":1000,
                "value":1,
                "step":1
            }),
        }