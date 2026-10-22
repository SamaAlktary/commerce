from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Bid, Category, Comment, Listing, User


def index(request):
  active_listings = Listing.objects.filter(is_active=True)
  return render(request, "auctions/index.html", {"listings": active_listings})


@login_required
def create_listing(request):
  if request.method == "POST":
    title = request.POST["title"]
    description = request.POST["description"]
    price = request.POST["price"]
    image_url = request.POST.get("image_url", "")
    category_id = request.POST.get("category")

    category = None
    if category_id:
      category = Category.objects.get(pk=category_id)

    Listing.objects.create(
        title=title,
        description=description,
        price=price,
        image_url=image_url,
        category=category,
        owner=request.user,
    )
    return HttpResponseRedirect(reverse("index"))

  categories = Category.objects.all()
  return render(request, "auctions/create.html", {"categories": categories})


@login_required
def listing_page(request, listing_id):
  listing = get_object_or_404(Listing, pk=listing_id)

  in_watchlist = False
  if request.user.is_authenticated:
    in_watchlist = request.user.watchlist.filter(pk=listing.id).exists()

  # تحديد أعلى مزايدة وصاحبها
  highest_bid = listing.bids.order_by("-bid").first()
  is_winner = False
  if not listing.is_active and highest_bid and highest_bid.user == request.user:
    is_winner = True

  if request.method == "POST":
    # 1. إغلاق المزاد
    if "close_auction" in request.POST and request.user == listing.owner:
      listing.is_active = False
      listing.save()
      return redirect("listing_page", listing_id=listing.id)

    # 2. تقديم مزايدة
    elif "bid_amount" in request.POST and listing.is_active:
      try:
        bid_amount = float(request.POST["bid_amount"])
      except ValueError:
        return render(
            request,
            "auctions/listing.html",
            {
                "listing": listing,
                "in_watchlist": in_watchlist,
                "comments": listing.comments.all(),
                "is_winner": is_winner,
                "message": "Invalid bid amount.",
            },
        )

      current_price = listing.price
      if highest_bid:
        current_price = highest_bid.bid

      if bid_amount > current_price:
        Bid.objects.create(bid=bid_amount, user=request.user, listing=listing)
        listing.price = bid_amount
        listing.save()
        return redirect("listing_page", listing_id=listing.id)
      else:
        return render(
            request,
            "auctions/listing.html",
            {
                "listing": listing,
                "in_watchlist": in_watchlist,
                "comments": listing.comments.all(),
                "is_winner": is_winner,
                "message": "Bid must be higher than current price.",
            },
        )

    # 3. إضافة تعليق
    elif "comment_message" in request.POST:
      message = request.POST["comment_message"]
      if message.strip():
        Comment.objects.create(
            message=message, user=request.user, listing=listing
        )
      return redirect("listing_page", listing_id=listing.id)

  return render(
      request,
      "auctions/listing.html",
      {
          "listing": listing,
          "in_watchlist": in_watchlist,
          "comments": listing.comments.all(),
          "is_winner": is_winner,
      },
  )


@login_required
def toggle_watchlist(request, listing_id):
  listing = get_object_or_404(Listing, pk=listing_id)
  if request.user.watchlist.filter(pk=listing.id).exists():
    request.user.watchlist.remove(listing)
  else:
    request.user.watchlist.add(listing)
  return redirect("listing_page", listing_id=listing.id)


@login_required
def watchlist_page(request):
  listings = request.user.watchlist.all()
  return render(request, "auctions/watchlist.html", {"listings": listings})


def categories_list(request):
  categories = Category.objects.all()
  return render(
      request, "auctions/categories.html", {"categories": categories}
  )


def category_page(request, category_id):
  category = get_object_or_404(Category, pk=category_id)
  listings = category.listings.filter(is_active=True)
  return render(
      request,
      "auctions/category_detail.html",
      {"category": category, "listings": listings},
  )


def login_view(request):
  if request.method == "POST":
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
      login(request, user)
      return HttpResponseRedirect(reverse("index"))
    else:
      return render(
          request,
          "auctions/login.html",
          {"message": "Invalid username and/or password."},
      )
  else:
    return render(request, "auctions/login.html")


def logout_view(request):
  logout(request)
  return HttpResponseRedirect(reverse("index"))


def register(request):
  if request.method == "POST":
    username = request.POST["username"]
    email = request.POST["email"]
    password = request.POST["password"]
    confirmation = request.POST["confirmation"]
    if password != confirmation:
      return render(
          request, "auctions/register.html", {"message": "Passwords must match."}
      )
    try:
      user = User.objects.create_user(username, email, password)
      user.save()
    except IntegrityError:
      return render(
          request,
          "auctions/register.html",
          {"message": "Username already taken."},
      )
    login(request, user)
    return HttpResponseRedirect(reverse("index"))
  else:
    return render(request, "auctions/register.html")