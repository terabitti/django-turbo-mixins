from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
)
from turbo import TurboDeleteViewMixin, TurboFormViewMixin, TurboViewMixin
from .forms import CategoryForm, ItemForm
from .models import Category, Item


class CategoryListView(ListView):
    model = Category

    def get_context_data(self):
        context = super().get_context_data()
        context["category_add_form"] = CategoryForm()
        context["is_category_limit_exceeded"] = Category.is_category_limit_exceeded()
        return context


class CategoryDetailView(TurboViewMixin, DetailView):
    model = Category


class CategoryCreateView(TurboFormViewMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "groceries/category_add.html"
    success_url = reverse_lazy("category-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["new_category_add_form"] = self.form_class()
        return context


class CategoryUpdateView(TurboFormViewMixin, UpdateView):
    queryset = Category.objects.all()
    form_class = CategoryForm

    # Demonstrate how to disable "success" template.
    success_template_name = None


class CategoryDeleteView(TurboDeleteViewMixin, DeleteView):
    queryset = Category.objects.all()
    success_url = reverse_lazy("category-list")

    def get_success_context_data(self):
        # Demonstates how we can control everything from the backend.
        # This re-enables category add form if limit is not exceeded anymore.
        # Of course this migth be better to be implemented in JavaScript.
        #
        # When total count is equal to 'max_categories' we know that after
        # delete there's one less. This is used in "success" template.
        context = super().get_success_context_data()
        if Category.objects.count() == Category.max_categories:
            context["new_category_add_form"] = CategoryForm()
        return context


class ItemDetailView(TurboViewMixin, DetailView):
    model = Item


class ItemCreateView(TurboFormViewMixin, CreateView):
    form_class = ItemForm
    template_name = "groceries/item_add.html"

    def get_success_url(self):
        return reverse("category", args=(self.object.category.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = Category.objects.get(pk=self.kwargs["category_id"])
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial["category"] = self.kwargs["category_id"]
        return initial


class ItemUpdateView(TurboFormViewMixin, UpdateView):
    queryset = Item.objects.all()
    form_class = ItemForm


class ItemDeleteView(TurboDeleteViewMixin, DeleteView):
    queryset = Item.objects.all()

    def get_success_url(self):
        return reverse("category", args=(self.object.category.id,))

    def get_success_context_data(self):
        # Demonstates how we can control everything from the backend.
        # This re-enables item add form if limit is not exceeded anymore.
        # Of course this migth be better to be implemented in JavaScript.
        #
        # When total count is equal to 'max_items' we know that after
        # delete there's one less. This is used in "success" template.
        context = super().get_success_context_data()
        category = self.object.category
        if category.item_set.count() == category.max_items:
            context["category"] = category
            context["new_item_add_form"] = category.get_item_add_form()
        return context
