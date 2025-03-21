from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listings/<int:id>", views.listings, name="listings"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories/", views.all_categories, name="all_categories"),
    path("categories/<str:name>", views.category, name="category")
]
