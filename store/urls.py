from django.urls import path
from store import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('products/', views.product_list_view, name='product_list'),
    path('products/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add_view, name='cart_add'),
    path('cart/update/', views.cart_update_view, name='cart_update'),
    path('cart/remove/<int:product_id>/', views.cart_remove_view, name='cart_remove'),
    path('cart/apply-coupon/', views.cart_apply_coupon_view, name='cart_apply_coupon'),
    path('cart/remove-coupon/', views.cart_remove_coupon_view, name='cart_remove_coupon'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/success/<str:order_number>/', views.order_success_view, name='order_success'),
    path('orders/', views.order_history_view, name='order_history'),
    path('orders/<str:order_number>/', views.order_detail_view, name='order_detail'),
    path('accounts/register/', views.user_register_view, name='register'),
    path('accounts/login/', views.user_login_view, name='login'),
    path('accounts/logout/', views.user_logout_view, name='logout'),
    path('accounts/profile/', views.user_profile_view, name='user_profile'),
]
