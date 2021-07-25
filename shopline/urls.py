from django.urls import path
from . import views

app_name = 'shopline'

urlpatterns =[
    path('register', views.register_user, name="register_user"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('login', views.login_user, name="login_user"),
    path('logout', views.logout_user, name="logout_user"),
    path('register-merchant', views.register_merchant, name="register_merchant"),
    path('dashboard/products/create', views.product_create, name="product_create"),
    path('dashboard/products', views.dashboard_products, name="dashboard_products"),
    path('dashboard/products/<int:id>/edit', views.product_edit,name="product_edit"),
    path('dashboard/products/<int:id>/delete', views.product_delete, name="product_delete"),
    path('dasboard/products/<int:id>/gallery', views.product_gallery, name='product_gallery'),
    path('gallery/<int:id>/delete', views.product_gallery_delete, name="product_gallery_delete"),
    path('', views.index, name='index'),
    path('products/<str:slug>', views.product_show, name="product_show"),
    path('cart/add', views.add_cart_item, name="add_cart_item"),
    path('cart', views.cart, name="cart"),
    path('cart/delete/<int:id>',views.delete_cart_item, name="delete_cart_item"),
    path('order', views.order, name="order"),
    path('checkout', views.checkout, name='checkout'),
]
