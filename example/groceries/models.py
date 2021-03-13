from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _


class Category(models.Model):
    name = models.CharField(_("name"), max_length=200)

    max_categories = 6
    max_items = 6

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category", args=[str(self.id)])

    def get_item_add_form(self):
        from .forms import ItemForm

        return ItemForm(initial={"category": self})

    @classmethod
    def is_category_limit_exceeded(cls):
        return cls.objects.count() >= cls.max_categories

    def is_item_limit_exceeded(self):
        return self.item_set.count() >= self.max_items


class Item(models.Model):
    name = models.CharField(_("name"), max_length=200)
    price = models.DecimalField(_("price"), max_digits=8, decimal_places=2)
    category = models.ForeignKey(
        Category,
        verbose_name=_("category"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("item", args=[str(self.category.id), str(self.id)])
