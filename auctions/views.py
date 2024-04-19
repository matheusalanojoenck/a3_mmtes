from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import *


def index(request):
    if request.method == "GET":
        activeListings = Listing.objects.filter(isActive=True)
    else:
        if request.POST["category"] != "":
            selectedCategory = Category.objects.get(categoryName=request.POST["category"])
            if selectedCategory in list(Category.objects.all()):
                category = Category.objects.get(categoryName=selectedCategory)
                activeListings = Listing.objects.filter(isActive=True, category=category)
            else:
                activeListings = Listing.objects.filter(isActive=True)
                print("index todos os itens")
        else:
            activeListings = Listing.objects.filter(isActive=True)

    allCategories = Category.objects.all()
    return render(
        request,
        "auctions/index.html",
        {"listings": activeListings, "categories": allCategories},
    )


def watchlist(request):
    userId = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html",{
        "listings": userId,
    })


def listing(request, listingId):
    listing = Listing.objects.get(pk=listingId)

    if request.method == "POST":
        if "addWatchlist" in request.POST:
            listing.watchlist.add(request.user)
        elif "removeWathclist" in request.POST:
            listing.watchlist.remove(request.user)
        elif "addComment" in request.POST:
            comment = request.POST["comment"]
            author = request.user
            newComment = Comment(
                author=author,
                listing=listing,
                comment=comment
            )
            newComment.save()
        elif "placeBid" in request.POST:

            try:
                bid = float(request.POST["bid"])
            except:
                bid = 0.00

            if (bid > listing.price) and (listing.owner != request.user):
                newBid = Bid(
                    user=request.user,
                    listing=listing,
                    bid=bid
                )
                newBid.save()
                listing.price = bid
                listing.save()
            else:
                print("bid invalido")
        elif "closeAuction" in request.POST:
            lastBid = Bid.objects.filter(listing=listing).latest('pk')
            listing.winner = lastBid.user
            listing.isActive = False
            listing.save()
        elif "openAuction" in request.POST:
            listing.isActive = True
            listing.save()

    inWatchlist = ""
    if request.user in listing.watchlist.filter():
        inWatchlist = True
    else:
        inWatchlist = False

    return render(
        request,
        "auctions/listing.html",
        {"listing": listing,
        "inWatchlist": inWatchlist,
        "comments": Comment.objects.filter(listing=listing),
        "bids": reversed(Bid.objects.filter(listing=listing))
        })


def createListing(request):
    if request.method == "GET":
        allCategories = Category.objects.all()
        return render(request, "auctions/create.html", {"categories": allCategories})
    else:
        title = request.POST["title"]
        description = request.POST["description"]
        imageurl = request.POST["imageurl"]

        try:
            price = float(request.POST["price"])
        except:
            price = 0.00

        category = Category.objects.get(categoryName=request.POST["category"])
        currentUser = request.user

        newListing = Listing(
            title=title,
            description=description,
            imageUrl=imageurl,
            price=price,
            category=category,
            owner=currentUser,
        )

        newListing.save()

        return HttpResponseRedirect(reverse(index))


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

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
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
