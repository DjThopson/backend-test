from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
 

urlpatterns = [
    # Path de control de sesión
    path('logout/', views.logoutpage,name='logout'),
    path('signin/', views.loginpage, name='loginpage'),

    # Path inicial
    path('menu/', views.main, name='main'),
    path('menu/<str:pk>', views.getMenu, name='get_menu'),

    # Path para el administrador
    path('create_menu/', views.createMenu, name='create_menu'),
    path('create_options/', views.createOptions, name='create_options'),
    path('create_dishes/', views.createDishes, name='create_dishes'),
    path('create_shopper/', views.createShopper, name="create_shopper"),

    # Path para órdenes
    path('create_order/<str:pk>/', views.createOrder, name='create_order'),
    path('edit_order/<str:pk>/', views.editOrder, name='edit_order'),
    path('drop_order/<str:pk>/', views.dropOrder, name='drop_order')
]