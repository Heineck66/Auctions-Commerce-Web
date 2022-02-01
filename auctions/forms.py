from django.db.models import fields
from auctions.models import Listing, Category
from typing import Sized
from django import forms
from django.forms import widgets


class ListingForm(forms.ModelForm):

    class Meta:
        model = Listing
        fields = ['short_name', 'description', 'picture', 'starting_value', 'categories']

    short_name = forms.CharField(label='Name ', max_length=18, widget=forms.TextInput(attrs={'class': "form-control formfield"}), required=True)
    description = forms.CharField(label='Description ', max_length=92, widget=forms.TextInput(attrs={'class': "form-control", 'style': "width: 350px;"}))
    picture = forms.CharField(label='Image URL', required=False)
    starting_value = forms.FloatField(label='Starting bid')

    categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), widget=forms.CheckboxSelectMultiple)

    picture.widget.attrs.update({'class': 'form-control formfield'})
    starting_value.widget.attrs.update({'class': 'form-control formfield'})
    # categories.widget.attrs.update({'class': 'form-control formfield'})

    #id_category .categorychoice


class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(attrs={'class': "form-control commentfield", 'placeholder': 'Leave your comment here.'}), label='', max_length=920)
