from django.core.exceptions import ValidationError
from django.forms import ModelForm, HiddenInput
from django.utils.translation import gettext as _
from .models import Category, Item


class PlaceholderMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["placeholder"] = field.label


class CategoryForm(PlaceholderMixin, ModelForm):
    class Meta:
        model = Category
        fields = ["name"]

    def clean(self):
        if self.instance.pk is None:
            if Category.is_category_limit_exceeded():
                raise ValidationError(
                    _("Maximum limit of categories exceeded."), code="limit"
                )
        super().clean()


class ItemForm(PlaceholderMixin, ModelForm):
    class Meta:
        model = Item
        fields = ["name", "price", "category"]
        widgets = {"category": HiddenInput()}

    def clean(self):
        cleaned_data = super().clean()
        if self.instance.pk is None:
            if cleaned_data["category"].is_item_limit_exceeded():
                raise ValidationError(
                    _("Maximum limit of items exceeded."), code="limit"
                )
