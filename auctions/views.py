import queue
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Auctions, Bids, Comments, Wishlist


def index(request):
    return render(request, "auctions/index.html", {
        "auctions": Auctions.objects.all()
    })


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
def create(request):
    if request.method == "GET":
        return render(request, "auctions/create.html")
    
    if request.method == "POST":
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        image = request.POST['image']
        user = request.user
        
        try:
            item = Auctions.objects.create(user=user, name=f"{name}", description=f"{description}", image=f"{image}", price=f"{price}")

            return HttpResponseRedirect(reverse(index))
        
        except IntegrityError:
            return render(request, "auctions/create.html", {
                "message": "There was an error creating your listing, Try again."
            })
            
def listings(request, name):
    listings = Auctions.objects.all()
    listings_lower = [listing.name.lower() for listing in listings]
    
    if request.method == "GET":
        if name.lower() in listings_lower:
            for listing in listings:
                if listing.name.lower() == name.lower():
                    q = listing

            return render(request, "auctions/listings.html",{
                "listing": q
            })
        
        else:
            return HttpResponseRedirect(reverse(index), {
                "message": "Listing not found"
            })
            
    if request.method == "POST":
        if 'wishlist' in request.POST:
            user = request.user
            item = request.POST['id']
            auction = Auctions.objects.get(pk=item)
            
            try:
                Wishlist.objects.create(user=user, item=auction)
                
                return HttpResponseRedirect(reverse(index), {
                "message": "Item added to your Wishlist"
            })
            except IntegrityError:
                return render(request, "auctions/listings.html", {
                    "message": "There was an error adding the item to your wishlist. Try again."
                })