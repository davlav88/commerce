from unicodedata import category
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

import auctions

from .models import User, Auctions, Bids, Comments, Watchlist, Winners, Categories

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
    

@login_required
def create(request):
    if request.method == "GET":
        message = request.GET.get('message')
        
        return render(request, "auctions/create.html", {
            "categories": Categories.objects.all(),
            "message":message
        })
    
    if request.method == "POST":
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        image = request.POST['image']
        category_input = request.POST['category']
        category = Categories.objects.get(name=category_input)
        user = request.user
        status = "open"
        
        if type(price) == int and price > 0:
            Auctions.objects.create(user=user, name=f"{name}", description=f"{description}", image=f"{image}", price=f"{price}", category=category)
        else:
            message = "Price must be a positive integer"
            
            return HttpResponseRedirect(f'/create?message={message}')

        return render(request, "auctions/index.html", {
                "message": "Auction created",
                "auctions": Auctions.objects.all()
            })
        
@login_required          
def listings(request, id):
        
    if request.method == "GET":
        q = Auctions.objects.get(pk=id)
        message = request.GET.get('message')
        creator = User.objects.get(id=q.user.id)
        
        try:
            winner = Winners.objects.get(item__id=id).user
        except Winners.DoesNotExist:
            winner = "No winner yet"
            
        try:
            highest_bid = Bids.objects.filter(item__id=id).order_by('-price').first()
        except highest_bid.DoesNotExist:
            highest_bid = "No bids yet"

            
        try:
            comments = Comments.objects.filter(item__id=id)
        except Winners.DoesNotExist:
            comments = "No comments yet"    
                
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
                "creator": creator,
                "winner": winner,
                "comments":comments,
                "highest_bid": highest_bid,
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
        bid_amount = request.POST['bid_amount']
        
        if type(bid_amount) == int and bid_amount > 0:
        
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
        else: 
            return HttpResponseRedirect(f'/listings/{id}?message=Bid must be a positive integer')
            
    if request.method == "POST" and 'close-auction' in request.POST:
        q = Auctions.objects.get(pk=id)
        highest_bid = Bids.objects.order_by('-price').first()
        winner = highest_bid.user

        try:
            q.status = "closed"
            q.save()

            Winners.objects.create(user=winner, item=q)
            
            
        except IntegrityError:
            pass
                        
    if request.method == "POST" and 'submit_comment' in request.POST:
        body = request.POST['comment']
        user = request.user
        q = Auctions.objects.get(pk=id)

        
        try:
            Comments.objects.create(user=user,comment=body, item=q)
        except IntegrityError:
            return HttpResponseRedirect(f'/listings/{id}?message=Invalid comment')

        

    
    return HttpResponseRedirect(reverse("index"))
        
        
@login_required               
def watchlist(request):
    if request.method == "GET":
        user = request.user
        
        return render(request, "auctions/watchlist.html", {
            "auctions": Watchlist.objects.filter(user=user)
        })
        
@login_required
def all_categories(request):
    try:
        categories = Categories.objects.all()
    except categories.DoesNotExist:
        categories = "No categories"
                                
    return render(request,"auctions/categories.html", {
        "categories":categories
    })
    
@login_required
def category(request,name):
    message = ""
    category = Categories.objects.get(name=name)
    if not category:
        message = "Category doesn't exist"
    
    auctions = Auctions.objects.filter(category__name=name)
    if not auctions:
        message = "No auctions for that category"
        
    return render(request,"auctions/category.html", {
        "auctions":auctions,
        "category":category,
        "message":message
    })
    
