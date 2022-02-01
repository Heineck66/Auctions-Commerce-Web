from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('login/', views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("categories", views.setcategories, name="categories"),
    path("categories/<str:category>", views.category, name="category"),
    path("watchlist", views.watch, name="watchlist"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("bid", views.bid, name="bid"),
    path('comments', views.comments, name='comments'),
    path('close', views.close, name='close')
]
