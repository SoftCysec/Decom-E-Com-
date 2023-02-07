from django.urls import path, re_path
#from django.conf.urls import url
from .views import OrderSummaryView, CheckoutView
from . import views

app_name = 'core'


urlpatterns = [
    path('cart/', OrderSummaryView.as_view(), name='cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('aboutus', views.aboutus_view, name='aboutus'),
    path('contactus', views.contactus_view,name='contactus'),
    path('', views.item_list, name='store'),
    #path('search/', views.search_product,name="search"),
    path('shop/<slug:category_slug>/', views.category_list, name='category_list'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<slug>/', views.add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', views.remove_from_cart, name="remove-from-cart"),
    path('remove-single-item/<slug>/', views.remove_single_item_from_cart,
        name='remove-single-item-from-cart'),

]