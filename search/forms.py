from django import forms

class SearchForm(forms.Form):
    address = forms.CharField(label='address', max_length=100)
    cityStateZip = forms.CharField(label='cityStateZip', max_length=100)
