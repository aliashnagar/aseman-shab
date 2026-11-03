from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"), path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"), path("panel/", views.dashboard, name="dashboard"),
    path("panel/products/", views.product_list, name="product_list"),
    path("panel/categories/", views.category_list, name="category_list"),
    path("panel/products/new/", views.product_edit, name="product_add"),
    path("panel/products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("panel/products/<int:pk>/toggle/", views.product_toggle, name="product_toggle"),
    path("panel/products/<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("panel/orders/", views.order_list, name="order_list"),
    path("track/", views.track_order, name="track_order"),
    path("api/products/", views.products_api, name="products_api"),
]
