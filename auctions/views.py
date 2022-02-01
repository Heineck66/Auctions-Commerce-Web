from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Category, Comment, User, Listing, Watchitem, Bid
from .forms import ListingForm, CommentForm


def index(request):
    listings = Listing.objects.exclude(closed=True)
    return render(
        request,
        "auctions/index.html",
        {
            "listings": listings,
        },
    )


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {"message": "Invalid username and/or password."})
    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {"message": "Passwords must match."})

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name.capitalize()
            user.last_name = last_name.capitalize()
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {"message": "Username already taken."})
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))
        return render(request, "auctions/register.html")


@login_required
def create(request):
    if request.method == "POST":
        form = ListingForm(request.POST)

        if form.is_valid:
            s_name = request.POST["short_name"]
            description = request.POST["description"]
            s_value = request.POST["starting_value"]
            seller = request.user
            date = datetime.today()
            picture = request.POST["picture"]
            cat_select = request.POST.getlist("categories")

            if request.POST["picture"] == "":
                picture = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/600px-No_image_available.svg.png"

            listing = Listing(
                short_name=s_name,
                description=description,
                starting_bid=s_value,
                seller=seller,
                create_date=date,
                picture=picture,
                higher_bid=s_value,
                buyer=seller,
            )
            listing.save()
            listing.categories.set(cat_select)
            messages.add_message(request, messages.INFO, "Success, created")
            return redirect("index")
        else:
            messages.add_message(request, messages.INFO, "Invalid form.")
            return redirect("create")

    form = ListingForm()
    categories = Category.objects.all()
    return render(
        request,
        "auctions/create.html",
        {
            "form": form,
            "categories": categories,
        },
    )


@login_required
def setcategories(request):
    categories = Category.objects.all()
    return render(
        request,
        "auctions/categories.html",
        {
            "categories": categories,
        },
    )


@login_required
def category(request, category):
    categories = Category.objects.all()
    category_id = Category.objects.all().get(category=category).id
    listings = Listing.objects.exclude(closed=True).filter(categories=category_id)

    return render(request, "auctions/category.html", {"categories": categories, "listings": listings})


@login_required
def watch(request):
    watchlist = Watchitem.objects.all().filter(user=request.user.id)

    return render(request, "auctions/watchlist.html", {"watchlist": watchlist})


def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    watch = Watchitem.objects.filter(user=request.user.id, listing=listing_id)
    if len(watch) > 0:
        isWatched = True
    else:
        isWatched = False

    # Set bids
    bids_count = listing.bid_set.all().count()
    if bids_count > 0:
        higher_bid = float(listing.bid_set.get(isHigherBid=True).value)
        bid_owner = listing.bid_set.get(isHigherBid=True).user
    else:
        higher_bid = listing.starting_bid
        bid_owner = listing.seller

    bid_info = {"higher_bid": higher_bid, "bids_count": bids_count, "bid_owner": bid_owner}

    # Get comments
    comments = Comment.objects.filter(listing=listing)
    commentform = CommentForm()

    if request.method == "POST":
        if not isWatched:
            newWatch = Watchitem(user=request.user, listing=Listing.objects.get(pk=listing_id))
            newWatch.save()
            isWatched = True

        else:
            Watchitem.objects.filter(user=request.user.id, listing=listing_id).delete()
            isWatched = False

    return render(
        request,
        "auctions/listing.html",
        {
            "listing": listing,
            "isWatched": isWatched,
            "bid_info": bid_info,
            "comments": comments,
            "commentform": commentform,
        },
    )


@login_required
def bid(request):
    listing_id = request.POST["listing_id"]
    listing = Listing.objects.get(pk=listing_id)

    if not listing.closed:
        new_value = float(request.POST["value"])
        buyer = request.user

        # Check if is the first bid
        if listing.bid_set.all().count() == 0:
            listing.higher_bid = new_value
            listing.save()
            bid = Bid(listing=listing, value=new_value, isHigherBid=True, date=datetime.today(), user=buyer)
            bid.save()

            messages.add_message(request, messages.INFO, "Bid made")
            return redirect("listing", listing_id=listing_id)

        else:
            actual_bid = listing.bid_set.get(isHigherBid=True)

            # For more than 1 bids
            if actual_bid.value < new_value:
                actual_bid.isHigherBid = False
                actual_bid.save()
                listing.higher_bid = new_value
                listing.save()
                bid = Bid(listing=listing, value=new_value, isHigherBid=True, date=datetime.today(), user=buyer)
                bid.save()
                print("Good!")
                messages.add_message(request, messages.INFO, "Bid made")
                return redirect("listing", listing_id=listing_id)
            else:
                print("Not valid")
                messages.add_message(request, messages.INFO, "Invalid Bid")
                return redirect("listing", listing_id=listing_id)

    messages.add_message(request, messages.INFO, "Auction Closed")
    return redirect("index")


@login_required
def comments(request):
    if request.method == "POST":
        form = CommentForm(request.POST)
        listing_id = request.POST["listing_id"]

        if form.is_valid:
            comment = request.POST["comment"]
            listing_id = request.POST["listing_id"]

            commentModel = Comment(
                listing=Listing.objects.get(pk=listing_id), comment=comment, date=datetime.today(), user=request.user
            )
            commentModel.save()

            messages.add_message(request, messages.INFO, " Comment Sent.")
            return redirect("listing", listing_id=listing_id)
        else:
            listing_id = request.POST["listing_id"]
            messages.add_message(request, messages.INFO, " Comment Invalid.")
            return redirect("listing", listing_id=listing_id)

    return HttpResponseRedirect(reverse("index"))


def close(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]

        listing = Listing.objects.get(pk=listing_id)
        listing.closed = True
        if listing.bid_set.all().count() > 0:
            listing.buyer = listing.bid_set.get(isHigherBid=True).user
        else:
            listing.buyer = request.user
        listing.save()

        messages.add_message(request, messages.INFO, "Auction Closed.")
        return redirect("listing", listing_id=listing_id)

    return HttpResponseRedirect(reverse("index"))
