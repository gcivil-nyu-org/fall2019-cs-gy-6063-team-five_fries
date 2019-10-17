from django import forms


class ZillowSearchForm(forms.Form):
    address = forms.CharField(label="address", max_length=100)
    city_state_zip = forms.CharField(label="cityStateZip", max_length=100)
