from django.contrib import admin
from django import forms
from django.forms import BaseInlineFormSet
from django.forms import ValidationError

from submission.models import Message


class MessageForm(forms.ModelForm):
    """Form for message to fill data."""

    def __init__(self, *args, parent_obj, request, **kwargs):
        """init."""
        self.parent_obj = parent_obj
        self.request = request
        super().__init__(*args, **kwargs)

    class Meta:
        """Meta class."""

        model = Message
        fields = "__all__"

    def clean(self):
        """For getting correct data."""
        data = self.cleaned_data
        sender = data.get("sender", None)
        if sender:
            if self.request.user.id != sender.id:
                raise ValidationError(
                    {"sender": "Sender must be logged Admin"},
                )
        else:
            raise ValidationError(
                {"sender": "Set required field"},
            )


class MyFormSet(BaseInlineFormSet):
    """Formset for MessageForm."""

    def __init__(self, *args, **kwargs):
        """init."""
        kwargs["initial"] = [
            {
                "sender": self.request.user,  # pylint: disable-msg=E1101
                "content": "",
            },
        ]
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        """To send request and parent_object."""
        kwargs = super().get_form_kwargs(index)
        kwargs["parent_obj"] = self.instance
        kwargs["request"] = self.request  # pylint: disable-msg=E1101
        return kwargs


class MessageInline(admin.TabularInline):
    """MessageInline for getting it in detailed PackageAdmin panel."""

    model = Message
    fields = ("sender", "timestamp", "content")
    readonly_fields = ("timestamp",)
    extra = 1
    formset = MyFormSet
    form = MessageForm

    def get_formset(self, request, obj=None, **kwargs):
        """To get formset."""
        formset = super().get_formset(request, obj, **kwargs)
        formset.request = request
        formset.parent_obj = obj
        return formset

    def has_change_permission(self, request, obj=None):
        """Has permission to change method."""
        return False


admin.site.register(Message)
