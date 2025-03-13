import queue
import re
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

import auctions

from .models import User, Auctions, Bids, Comments, Watchlist


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
            Auctions.objects.create(user=user, name=f"{name}", description=f"{description}", image=f"{image}", price=f"{price}")

            return render(request, "auctions/index.html", {
                "message": "Auction created",
                "auctions": Auctions.objects.all()
            })
        
        except IntegrityError:
            return render(request, "auctions/create.html", {
                "message": "There was an error creating your listing, Try again."
            })
            
def listings(request, id):
        
    if request.method == "GET":
        q = Auctions.objects.get(pk=id)
        message = request.GET.get('message')
        creator = q.user.id
        
        if q:
            w = Watchlist.objects.filter(item__id=id)
            if w:
                button = "Remove from Watchlist"   
            else:
                button = "Add to Watchlist"
            
            return render(request, "auctions/listings.html",{
                "listing": q,
                "button": button,
                "message": message,
                "creator": creator
            })
            
        else:
            return render(request, "auctions/listings.html",{
                "message": "Listing not found"
            })

            
    if request.method == "POST" and 'watchlist' in request.POST:
        user = request.user
        auction = Auctions.objects.get(pk=id)
        watchlist = Watchlist.objects.filter(user=user,item=auction)
        
        if not watchlist:
            try:
                Watchlist.objects.create(user=user, item=auction)
                
                return render(request, "auctions/listings.html", {
                "message": "Item added to your Watchlist",
                "listing": auction,
                "button": "Remove from Watchlist"
            })
            except IntegrityError:
                return render(request, "auctions/listings.html", {
                "message": "There was an error adding the item to your watchlist. Try again.",
                "listing": auction,
                "button": "Add to Watchlist"
            })
        else:
            try:
                watchlist.delete()
                
                return render(request, "auctions/listings.html", {
                    "message": "Item removed from Watchlist",
                    "listing": auction,
                    "button": "Add to Watchlist"
                })
            except IntegrityError:
                return render(request, "auctions/listings.html", {
                    "message": "There was an error removing the item from your watchlist. Try again.",
                    "listing": auction,
                    "button": "Remove from Watchlist"
                })
                
    if request.method == "POST" and 'bid' in request.POST:
        user = request.user
        auction = Auctions.objects.get(pk=id)
        bid_amount = int(request.POST['bid_amount'])
        
        bids = Bids.objects.filter(item__id=id)
        if bids:
            highest_bid = Bids.objects.order_by('-price').first()
            if bid_amount > highest_bid.price:
                Bids.objects.create(user=user,item=auction, price=bid_amount)
            else:
                return HttpResponseRedirect(f'/listings/{id}?message=Bid too low')

        else:
            if bid_amount >= int(auction.price):
                Bids.objects.create(user=user,item=auction, price=bid_amount)
            else:
                return HttpResponseRedirect(f'/listings/{id}?message=Bid too low')
            
    if request.method == "POST" and 'close-auction' in request.POST:
        q = Auctions.objects.get(pk=id)
        highest_bid = Bids.objects.order_by('-price').first()
        winner = highest_bid.user
        print("clicked")
        print(q.status)
        try:
            q.status = "closed"
            q.save()
        except IntegrityError:
            pass
                        
    return HttpResponseRedirect(reverse("index"))
        
        
                
def watchlist(request):
    if request.method == "GET":
        user = request.user
        
        return render(request, "auctions/watchlist.html", {
            "auctions": Watchlist.objects.filter(user=user)
        })