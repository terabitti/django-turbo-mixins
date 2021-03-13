from django.urls import path
from . import views


urlpatterns = [
    path("", views.CategoryListView.as_view(), name="category-list"),
    path("categories/add/", views.CategoryCreateView.as_view(), name="category-add"),
    path("categories/<pk>/", views.CategoryDetailView.as_view(), name="category"),
    path(
        "categories/<pk>/edit/",
        views.CategoryUpdateView.as_view(),
        name="category-edit",
    ),
    path(
        "categories/<pk>/delete/",
        views.CategoryDeleteView.as_view(),
        name="category-delete",
    ),
    path(
        "categories/<int:category_id>/items/add/",
        views.ItemCreateView.as_view(),
        name="item-add",
    ),
    path(
        "categories/<int:category_id>/items/<pk>/",
        views.ItemDetailView.as_view(),
        name="item",
    ),
    path(
        "categories/<int:category_id>/items/<pk>/edit/",
        views.ItemUpdateView.as_view(),
        name="item-edit",
    ),
    path(
        "categories/<int:category_id>/items/<pk>/delete/",
        views.ItemDeleteView.as_view(),
        name="item-delete",
    ),
]
