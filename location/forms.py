from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Button, ButtonHolder, Div

from localflavor.us import forms as us_forms
from .models import Location, Apartment, ClaimRequest, OtherImages
from external.googleapi.fetch import fetch_geocode
from external.googleapi import g_utils


class ApartmentUploadForm(forms.Form):

    city = forms.CharField(label="City", max_length=100)
    state = us_forms.USStateField(label="State")
    address = forms.CharField(label="Address", max_length=255)
    zipcode = us_forms.USZipCodeField(label="Zip Code")
    rent_price = forms.DecimalField(
        label="Rent Price ($)",
        max_digits=20,
        decimal_places=2,
        validators=[MinValueValidator(1), MaxValueValidator(100000)],
    )
    number_of_bed = forms.IntegerField(
        label="Bedrooms", validators=[MinValueValidator(0), MaxValueValidator(10)]
    )

    # Handling input files with Django
    # https://simpleisbetterthancomplex.com/tutorial/2016/08/01/how-to-upload-files-with-django.html
    image = forms.ImageField()
    suite_num = forms.CharField(label="Suite Number", max_length=30)
    description = forms.CharField(widget=forms.Textarea)

    def clean_suite_num(self):
        """checks for apartments with duplicate suite numbers in the same location"""
        city = self.cleaned_data.get("city")
        state = self.cleaned_data.get("state")
        address = self.cleaned_data.get("address")
        zipcode = self.cleaned_data.get("zipcode")
        suite_num = self.cleaned_data.get("suite_num")

        if suite_num.strip()[0] == "-":
            raise forms.ValidationError(
                "You cannot submit an apartment with a negative Suite Number"
            )

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

    def clean(self):
        super(ApartmentUploadForm, self).clean()

        address = self.cleaned_data.get("address")
        city = self.cleaned_data.get("city")
        state = self.cleaned_data.get("state")
        zipcode = self.cleaned_data.get("zipcode")

        g_data = fetch_geocode(f"{address}, {city} {state}, {zipcode}")
        if len(g_data) == 0:
            raise forms.ValidationError(
                "Unable to locate that address, please check that it was entered correctly."
            )

        g_address = g_utils.get_address(g_data)
        g_city = g_utils.get_city(g_data)[0]
        g_state = g_utils.get_state(g_data)
        g_zip = g_utils.get_zipcode(g_data)

        if g_city.lower() != city.lower():
            self.add_error(
                "city",
                f"The input value of {city} did not match the resolved value of {g_city}",
            )
        if g_state != state:
            self.add_error(
                "state",
                f"The input value of {state} did not match the resolved value of {g_state}",
            )
        if g_zip != zipcode:
            self.add_error(
                "zipcode",
                f"The input value of {zipcode} did not match the resolved value of {g_zip}",
            )
        if g_address[0].lower() not in address.lower():
            self.add_error(
                "address",
                f"The input value of {address} did not contain the resolved value {g_address[0]}",
            )
        if g_address[1].lower() not in address.lower():
            self.add_error(
                "address",
                f"The input value of {address} did not contain the resolved value {g_address[1]}",
            )


class ImageForm(forms.ModelForm):
    image = forms.ImageField(label="Extra Image")

    class Meta:
        model = OtherImages
        fields = ("image",)


class ClaimForm(forms.ModelForm):
    class Meta:
        model = ClaimRequest
        exclude = ["allow_token", "deny_token", "access_granted"]

    def __init__(self, *args, **kwargs):
        super(ClaimForm, self).__init__(*args, **kwargs)
        self.fields["user"].widget = forms.HiddenInput()
        self.fields["apartment"].widget = forms.HiddenInput()

    def clean(self):
        super(ClaimForm, self).clean()
        request_type = self.cleaned_data.get("request_type")
        apartment = self.cleaned_data.get("apartment")
        if request_type == "tenant" and apartment and not apartment.landlord:
            raise forms.ValidationError(
                "This Apartment does not currently have a Landlord registered with the site"
            )


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

        if suite_num and suite_num.strip()[0] == "-":
            raise forms.ValidationError(
                "You cannot submit an apartment with a negative Suite Number"
            )

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
