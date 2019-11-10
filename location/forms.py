from django import forms
from localflavor.us import forms as us_forms

class ApartmentUploadForm(forms.Form):
    city = forms.CharField(label="City", max_length = 100)
    state = us_forms.USStateField(label="State")
    address = forms.CharField(label="Address", max_length=255)
    zipcode = us_forms.USZipCodeField(label="Zip Code")
    estimated_rent_price = forms.DecimalField(label="Rent Price ($)", max_digits=20, decimal_places=2)
    latitude = forms.DecimalField(
        label="Latitude", required = False, max_digits=9, decimal_places=6)
    longitude = forms.DecimalField(
        label="Longitude", required = False, max_digits=9, decimal_places=6)
    suite_num = forms.CharField(label="Suite Number", required = False, max_length=30)


    def clean_estimated_rent_price(self):
        estimated_rent_price = self.cleaned_data.get('estimated_rent_price')
        if estimated_rent_price < 0:
            raise forms.ValidationError("Rental price cannot be negative!")

        return estimated_rent_price