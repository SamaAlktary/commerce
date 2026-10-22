from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create_listing"),
    path("listing/<int:listing_id>", views.listing_page, name="listing_page"),
    path("watchlist", views.watchlist_page, name="watchlist"),
    path("watchlist/toggle/<int:listing_id>", views.toggle_watchlist, name="toggle_watchlist"),
    path("categories", views.categories_list, name="categories"),
    path("categories/<int:category_id>", views.category_page, name="category_page"),
]