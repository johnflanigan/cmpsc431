from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render
from menu.forms import AddItemForm, BrowseForm, SearchForm
from menu.models import Item
from orders.forms import PartialInitiateForm
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import user_passes_test
from decimal import Decimal

def supplier_check(user):
    return user.userprofile.supplier_flag

# add item view
@user_passes_test(supplier_check, login_url='/notsupplier/')
def add_menu_item(request):
    form = AddItemForm()

    if request.method == 'POST':
        form = AddItemForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return success(request)
        else:
            print(form.errors)

    return render(request, "menu/add_item.html", {'form': form})


# success view
def success(request):
    return render(request, 'menu/success.html')


# search view
def search(request):
    form = SearchForm()

    # if search form is submitted, go to results
    if request.method == 'POST':
        return searchresults(request)

    # else show blank form
    else:
        return render(request, 'menu/search.html', {'form': form})


# search results view
def searchresults(request):
    # get search parameters
    searchstring = request.POST.get('searchstring')
    is_food = request.POST.get('is_food')
    is_drink = request.POST.get('is_drink')
    is_breakfast = request.POST.get('is_breakfast')
    is_lunch = request.POST.get('is_lunch')

    # get food and drink states
    if (is_food and is_drink):
        FOOD = 'FOOD'
        DRINK = 'DRINK'
    elif (is_food):
        FOOD = 'FOOD'
        DRINK = -1
    elif (is_drink):
        FOOD = -1
        DRINK = 'DRINK'
    else:
        FOOD = 'FOOD'
        DRINK = 'DRINK'

    # filter and sort for each case
    if (is_breakfast and is_lunch):
        results = Item.objects.filter(
            name__icontains=searchstring).filter(
            Q(food_or_drink=FOOD)|Q(food_or_drink=DRINK)).order_by(
            '-promo_flag'
        )
    elif (is_breakfast and not is_lunch):
        results = Item.objects.filter(
            name__icontains=searchstring).filter(
            is_breakfast=True).filter(
            Q(food_or_drink=FOOD)|Q(food_or_drink=DRINK)).order_by(
            '-promo_flag'
        )
    elif (not is_breakfast and is_lunch):
        results = Item.objects.filter(
            name__icontains=searchstring).filter(
            is_lunch=True).filter(
            Q(food_or_drink=FOOD)|Q(food_or_drink=DRINK)).order_by(
            '-promo_flag'
        )
    else:
        results = Item.objects.filter(
            name__icontains=searchstring).filter(
            Q(food_or_drink=FOOD)|Q(food_or_drink=DRINK)).order_by(
            '-promo_flag'
        )

    context_dict = {'results': results}

    # render
    return render(request, 'menu/searchresults.html', context_dict)


# browse items view
def browse(request):
    form = BrowseForm()

    # if browse form submitted, go to results
    if request.method == 'POST':
        return browseresults(request)

    # else show blank form
    else:
        return render(request, 'menu/browse.html', {'form': form})


# browse results view
def browseresults(request):
    # get browse parameters
    restaurant_name = request.POST.get('restaurant_name')
    is_food = request.POST.get('is_food')
    is_drink = request.POST.get('is_drink')
    is_breakfast = request.POST.get('is_breakfast')
    is_lunch = request.POST.get('is_lunch')

    print(restaurant_name)
    print(is_food)
    print(is_drink)
    print(is_breakfast)
    print(is_lunch)

    # get food and drink states
    if (is_food and is_drink):
        FOOD = 'FOOD'
        DRINK = 'DRINK'
    elif (is_food):
        FOOD = 'FOOD'
        DRINK = -1
    elif (is_drink):
        FOOD = -1
        DRINK = 'DRINK'
    else:
        FOOD = 'FOOD'
        DRINK = 'DRINK'

    # filter and sort for each case
    if (is_breakfast and is_lunch):
        item_list = Item.objects.filter(
            supplier=restaurant_name).filter(
            Q(food_or_drink=FOOD)|Q(food_or_drink=DRINK)).order_by(
            '-promo_flag'
        )
    elif (is_breakfast and not is_lunch):
        item_list = Item.objects.filter(
            supplier=restaurant_name).filter(
            is_breakfast=True).filter(
            Q(food_or_drink=FOOD)|Q(food_or_drink=DRINK)).order_by(
            '-promo_flag'
        )
    elif (not is_breakfast and is_lunch):
        item_list = Item.objects.filter(
            supplier=restaurant_name).filter(
            is_lunch=True).filter(
            Q(food_or_drink=FOOD)|Q(food_or_drink=DRINK)).order_by(
            '-promo_flag'
        )
    else:
        item_list = Item.objects.filter(
            supplier=restaurant_name).filter(
            Q(food_or_drink=FOOD)|Q(food_or_drink=DRINK)).order_by(
            '-promo_flag'
        )

    print(item_list)

    context_dict = {'items': item_list}

    # render
    return render(request, 'menu/browseresults.html', context_dict)


# order item view
def orderitem(request):
    # get form and currently logged in user
    form = PartialInitiateForm()
    userid = request.user.id

    # if get, pull item id from request
    if request.method == 'GET':
        itemid = request.GET['itemid']

    # if post, submit request
    elif request.method == 'POST':
        # get itemid from request
        itemid = request.POST.get('itemid')
        item = Item.objects.get(id=itemid)
        initiates = User.objects.get(id=userid)

        form = PartialInitiateForm(request.POST)

        tip = Decimal(request.POST.get('tip'))
        wallet = initiates.userprofile.wallet
        quantity = int(request.POST.get('quantity'))
        price = item.price
        if tip + price*quantity > wallet:
           return render(request, 'menu/notenoughfunds.html')

        # save form but don't commit
        transaction = form.save(commit=False)

        # put userid and itemid into form
        transaction.initiates = initiates
        transaction.item = item

        # save form, commit
        transaction.save()

        # print errors
        print(form.errors)

        # show success page
        return success(request)

    # render open form
    return render(request, 'menu/orderitem.html', {'form': form, 'itemid' : itemid})
