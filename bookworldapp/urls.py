from django.urls import path
from . import views
from .views import *


urlpatterns = [
    path('',views.first,name='first'),

    path('contact', views.contactview,name='contact'),

    path('seller',views.sellerview,name='seller'),

    path('login',views.login,name='login'),

    path('logout',views.logout,name='logout'),

    path('signup',views.signup,name="signup"),

    path('search', views.search,name='search'),

    path('undergraduate',views.ug,name='undergraduate'),
    path('address',views.address,name='address'),
    path('order_summary/', order_summary.as_view(), name='order_summary'),
    path('cart/<slug>/',add_to_cart, name='cart'),
    path('remove/<slug>/',remove_from_cart, name='remove-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('payment',views.payment,name='payment'),
    path('payment_success',views.payment_success,name='payment_success'),


]
