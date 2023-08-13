from dataclasses import field
from typing import Any, Dict, Mapping, Optional, Type, Union

from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
import os
from django.core.exceptions import ValidationError


from .models import BynryUser, BynryUserProfile

def allow_only_images_validator(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = [".png", ".jpg", ".jpeg"]

    if not ext.lower() in valid_extensions:
        raise ValidationError(
            f"File type not supported, only {', '.join(valid_extensions)} are supported."
        )



class BynryUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = BynryUser
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
            "password",
        ]

    def clean(self):
        cleaned_data = super(BynryUserForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")


class BynryUserProfileForm(forms.ModelForm):
    address = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "enter your address", "required": "required"}
        )
    )
    profile_picture = forms.FileField(
        widget=forms.FileInput(attrs={"class": "btn btn-info"}),
        validators=[allow_only_images_validator],
    )
    cover_photo = forms.FileField(
        widget=forms.FileInput(attrs={"class": "btn btn-info"}),
        validators=[allow_only_images_validator],
    )

    # ⚡ Make fields readonly method 1 basic
    # latitude = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}))
    # longitude = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}))

    class Meta:
        model = BynryUserProfile
        fields = [
            "profile_picture",
            "cover_photo",
            "address",
            "country",
            "state",
            "city",
            "pin_code",
            "latitude",
            "longitude",
        ]

    # ⚡ Make fields readonly method 1 basic

    def __init__(self, *args, **kwargs):
        super(BynryUserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field == "latitude" or field == "longitude":
                self.fields[field].widget.attrs["readonly"] = "readonly"


class BynryUserInfoForm(forms.ModelForm):
    class Meta:
        model = BynryUser
        fields = [
            "first_name",
            "last_name",
            "phone_number",
        ]
