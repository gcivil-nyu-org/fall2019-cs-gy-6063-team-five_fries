from allauth.account.adapter import DefaultAccountAdapter


class UserAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        """
        this is called when saving user via allauth registration.
        we override this to set additional data on user object
        """
        # do not persist the user yet so we pass commit=False
        # (last argument)
        """phone_number = forms.CharField(max_length=30)
    current_location = forms.CharField(max_length=30)
    work_location = forms.CharField(max_length=30)
    use_type = forms.ChoiceField("""

        user = super(UserAccountAdapter, self).save_user(
            request, user, form, commit=False
        )
        user.phone_number = form.cleaned_data.get("phone_number")
