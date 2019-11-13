from django import forms
from django.core import validators
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field


class SearchForm(forms.Form):
    zipcode = forms.CharField(
        max_length=5,
        min_length=5,
        required=True,
        validators=[
            validators.RegexValidator(
                regex="^\d*$", message="Please use numbers"
            )  # noqa : W605
        ],
    )
    min_price = forms.IntegerField(min_value=0, required=False)
    max_price = forms.IntegerField(min_value=0, required=False)
    bed_num = forms.IntegerField(min_value=0, required=False)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()

        self.helper.form_method = "get"
        self.helper.form_action = "search"
        # add css classes to the form
        self.helper.form_class = "form-inline"
        self.helper.error_text_inline = True
        # adds css class to the labels
        self.helper.label_class = "sr-only"
        self.helper.field_template = "bootstrap4/layout/inline_field.html"
        self.helper.layout = Layout(
            Field(
                "zipcode",
                css_class="form-control-sm mb-2 mr-sm-2",
                placeholder="Zip Code",
            ),
            Field(
                "min_price",
                css_class="form-control-sm mb-2 mr-sm-2",
                placeholder="Min Price",
            ),
            Field(
                "max_price",
                css_class="form-control-sm mb-2 mr-sm-2",
                placeholder="Max Price",
            ),
            Field(
                "bed_num",
                css_class="form-control-sm mb-2 mr-sm-2",
                placeholder="Bedroom Number",
            ),
            Submit("search", "Go", css_class="btn btn-primary mb-2"),
        )
        super(SearchForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(SearchForm, self).clean()

        min_price = self.cleaned_data.get("min_price")
        max_price = self.cleaned_data.get("max_price")

        if min_price and max_price:
            if min_price > max_price:
                # adds error messages just to the fields
                # if we raise a Validation error the layout of the inline-form
                # is messed up
                self.add_error("min_price", "Larger than Max")
                self.add_error("max_price", "Less than Min")
