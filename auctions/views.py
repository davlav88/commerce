from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

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
            "message":message,
            "alert_class":"alert-danger"
        })
    
    if request.method == "POST":
        try:
            name = request.POST['name']
            description = request.POST['description']
            price = int(request.POST['price'])
            image = request.POST['image']
            category_input = request.POST['category']
            category = Categories.objects.get(name=category_input)
            user = request.user
            status = "open"
            
            if name and description and price:
                if price > 0:
                    Auctions.objects.create(user=user, name=f"{name}", description=f"{description}", image=f"{image}", price=f"{price}", category=category)
                    
                    return render(request, "auctions/index.html", {
                    "message": "Auction created",
                    "alert_class":"alert-success",
                    "auctions": Auctions.objects.all()
                })
                else:
                    message = "Price must be a positive integer"
                    return HttpResponseRedirect(reverse("create") + f"?message={message}")
                    
            else:
                message = "Incomplete listing"
                return HttpResponseRedirect(reverse("create") + f"?message={message}")
                
        except:
            message = "Error, try again"
            return HttpResponseRedirect(reverse("create") + f"?message={message}")
        

        
@login_required          
def listings(request, id):
        
    if request.method == "GET":
        q = Auctions.objects.get(pk=id)
        message = request.GET.get('message')
        alert_class = request.GET.get('alert_class')
        creator = User.objects.get(id=q.user.id)
        
        try:
            winner = Winners.objects.get(item__id=id).user
        except Winners.DoesNotExist:
            winner = "No winner yet"
            
        highest_bid = Bids.objects.filter(item__id=id).order_by('-price').first()
        if highest_bid is None:
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
                "alert_class": alert_class,
                "creator": creator,
                "winner": winner,
                "comments":comments,
                "highest_bid": highest_bid,
            })
            
        else:
            return render(request, "auctions/listings.html",{
                "message": "Listing not found",
                "alert_class": "alert-danger"
            })

            
    if request.method == "POST" and 'watchlist' in request.POST:
        user = request.user
        auction = Auctions.objects.get(pk=id)
        watchlist = Watchlist.objects.filter(user=user,item=auction)
        
        if not watchlist:
            try:
                Watchlist.objects.create(user=user, item=auction)
                message = "Item added to your Watchlist"
                alert_class = "alert-success"
                return HttpResponseRedirect(f'/listings/{id}?message={message}&alert_class={alert_class}')

            except IntegrityError:
                message = "There was an error adding the item to your watchlist. Try again."
                alert_class = "alert-danger"
                return HttpResponseRedirect(f'/listings/{id}?message={message}&alert_class={alert_class}')

        else:
            try:
                watchlist.delete()
                message = "Item removed from Watchlist"
                alert_class = "alert-success"
                return HttpResponseRedirect(f'/listings/{id}?message={message}&alert_class={alert_class}')

            except IntegrityError:
                message = "There was an error removing the item from your watchlist. Try again."
                alert_class = "alert-danger"
                return HttpResponseRedirect(f'/listings/{id}?message={message}&alert_class={alert_class}')

                
    if request.method == "POST" and 'bid' in request.POST:
        user = request.user
        auction = Auctions.objects.get(pk=id)
        bid_amount = int(request.POST['bid_amount'])
        
        if bid_amount > 0:
        
            bids = Bids.objects.filter(item__id=id)
            if bids:
                highest_bid = Bids.objects.order_by('-price').first()
                if bid_amount > highest_bid.price:
                    Bids.objects.create(user=user,item=auction, price=bid_amount)
                else:
                    message = "Bid too low"
                    alert_class = "alert-warning"
                    return HttpResponseRedirect(f'/listings/{id}?message={message}&alert_class={alert_class}')

            else:
                if bid_amount >= int(auction.price):
                    Bids.objects.create(user=user,item=auction, price=bid_amount)
                else:
                    message = "Bid too low"
                    alert_class = "alert-warning"
                    return HttpResponseRedirect(f'/listings/{id}?message={message}&alert_class={alert_class}')
        else: 
            message = "Bid must be a positive integer"
            alert_class = "alert-warning"
            return HttpResponseRedirect(f'/listings/{id}?message={message}&alert_class={alert_class}')
            
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
            message = "Invalid comment"
            alert_class = "alert-danger"
            return HttpResponseRedirect(f'/listings/{id}?message={message}&alert_class={alert_class}')

    return HttpResponseRedirect(f'/listings/{id}')
        
        
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
    alert_class = ""
    category = Categories.objects.get(name=name)
    if not category:
        message = "Category doesn't exist"
        alert_class = "alert-warning"
    
    auctions = Auctions.objects.filter(category__name=name)
    if not auctions:
        message = "No auctions for that category"
        alert_class = "alert-warning"

        
    return render(request,"auctions/category.html", {
        "auctions":auctions,
        "category":category,
        "message":message,
        "alert_class": alert_class
    })
    
