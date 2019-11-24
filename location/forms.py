from django import forms
from django.core.validators import MinValueValidator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Button, ButtonHolder, Div

from localflavor.us import forms as us_forms
from .models import Location, Apartment


class ApartmentUploadForm(forms.Form):

    city = forms.CharField(label="City", max_length=100)
    state = us_forms.USStateField(label="State")
    address = forms.CharField(label="Address", max_length=255)
    zipcode = us_forms.USZipCodeField(label="Zip Code")
    rent_price = forms.DecimalField(
        label="Rent Price ($)", max_digits=20, decimal_places=2
    )
    number_of_bed = forms.IntegerField(
        label="Bedrooms", validators=[MinValueValidator(0)]
    )

    # Handling input files with Django
    # https://simpleisbetterthancomplex.com/tutorial/2016/08/01/how-to-upload-files-with-django.html
    image = forms.ImageField()
    suite_num = forms.CharField(label="Suite Number", max_length=30)
    description = forms.CharField(widget=forms.Textarea)

    def clean_rent_price(self):
        rent_price = self.cleaned_data.get("rent_price")
        if rent_price < 0:
            raise forms.ValidationError("Rental price cannot be negative!")

        return rent_price

    def clean_suite_num(self):
        """checks for apartments with duplicate suite numbers in the same location"""
        city = self.cleaned_data.get("city")
        state = self.cleaned_data.get("state")
        address = self.cleaned_data.get("address")
        zipcode = self.cleaned_data.get("zipcode")
        suite_num = self.cleaned_data.get("suite_num")
        try:  # If the apartment belongs to a location that already exists
            loc = Location.objects.get(
                city=city, state=state, address=address, zipcode=zipcode
            )
            try:
                Apartment.objects.get(suite_num=suite_num, location=loc)
                raise forms.ValidationError(
                    "An apartment with the same suite number already exists at this location! \
                    If you are the landlord, you can edit the apartment details by going to your account page."
                )
            except Apartment.DoesNotExist:
                return suite_num
        except Location.DoesNotExist:
            # if the apartment belongs to a location that does not exist, we can't have duplicate apartments
            return suite_num


class ClaimForm(forms.Form):
    claim_type = forms.ChoiceField(
        choices=[
            ("tenant", "I am a tenant of this apartment"),
            ("landlord", "I am a landlord of this apartment"),
        ],
        widget=forms.RadioSelect(attrs={"required": True}),
        label="Are you a tenant or a landlord?",
        required=True,
    )
    note = forms.CharField(widget=forms.Textarea, required=False)


class ContactLandlordForm(forms.Form):
    subject = forms.CharField(label="Subject", max_length=100)
    message = forms.CharField(label="Message", max_length=1000)


class ApartmentUpdateForm(forms.ModelForm):
    class Meta:
        model = Apartment
        exclude = ["location", "landlord", "tenant", "c_id", "zpid", "last_estimated"]

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            "is_rented",
            "suite_num",
            "rent_price",
            "number_of_bed",
            "description",
            "image",
            ButtonHolder(
                Div(
                    Div(
                        Submit("update", "Update", css_class="btn btn-primary"),
                        css_class="text-left",
                    ),
                    css_class="col col-sm-3",
                ),
                Div(
                    Div(
                        Button(
                            "delete",
                            "Delete",
                            css_class="btn btn-primary",
                            data_toggle="modal",
                            data_target="#deleteModal",
                        ),
                        css_class="text-left",
                    ),
                    css_class="col-sm-3",
                ),
                Div(
                    Div(
                        Button(
                            "cancel",
                            "Cancel",
                            css_class="btn btn-primary",
                            onclick="history.back()",
                        ),
                        css_class="text-right",
                    ),
                    css_class="col col-sm-6",
                ),
                css_class="row justify-content-between",
            ),
        )
        super(ApartmentUpdateForm, self).__init__(*args, **kwargs)

    def clean_suite_num(self):
        suite_num = self.cleaned_data.get("suite_num")
        # access the passed in instance of the Apartment model to get its location
        location = self.instance.location

        if (
            self.instance.suite_num != suite_num
            and Apartment.objects.filter(
                suite_num=suite_num, location=location
            ).exists()
        ):
            raise forms.ValidationError(
                "Another apartment exists at that location with that Suite number."
            )

        return suite_num
