from django.shortcuts import render
from orders.models import Transaction
from datetime import datetime
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test

def supplier_check(user):
    return user.userprofile.supplier_flag

# open requests view
def openrequests(request):

    # initialize context dictionary
    context_dict = {}

    # get unclaimed transactions
    transactions = Transaction.objects.filter(
        delivers__isnull=True)

    # update context dictionary
    context_dict['transactions'] = transactions

    # render
    return render(request, "orders/openrequests.html", context_dict)


# Pickup item button view
def pickupitem(request):

    # if button pressed
    if request.method == 'GET':

        # get transaction id and transaction
        transactionid = request.GET['transactionid']
        transaction = Transaction.objects.get(id=transactionid)

        # set deliverer in transaction
        transaction.delivers = request.user

        # save the form in the database
        transaction.save()

        # render success page
        return pickupsuccess(request)


# pickup success view
def pickupsuccess(request):
    return render(request, 'orders/pickupsuccess.html')


def myorders(request):
    # initialize context dictionary and grab userid
    context_dict = {}
    userid = request.user.id

    # find requests that matches that userid
    requests = Transaction.objects.filter(
        initiates__exact=userid).filter(
        delivery_time__isnull=True)
    context_dict['requests'] = requests

    # find deliveries that matches that userid
    deliveries = Transaction.objects.filter(
        delivers__exact=userid).filter(
        delivery_time__isnull=True)
    context_dict['deliveries'] = deliveries

    #render
    return render(request, "orders/myorders.html", context_dict)

def delivererexchange(request):
    if request.method == 'GET':
        context_dict = {}
        transactionid = request.GET['transactionid']
        transaction = Transaction.objects.get(id=transactionid)
        context_dict['transactions'] = transaction
        return render(request, "orders/delivererexchange.html", context_dict)

def recipientexchange(request):
    if request.method == 'GET':
        context_dict = {}
        transactionid = request.GET['transactionid']
        transaction = Transaction.objects.get(id=transactionid)
        context_dict['transactions'] = transaction
        return render(request, "orders/recipientexchange.html", context_dict)

    elif request.method == 'POST':
        transactionid = request.POST.get('transactionid')
        code = request.POST.get('code')
        timeliness = request.POST.get('timeliness')
        friendliness = request.POST.get('friendliness')
        responsetime = request.POST.get('responsetime')
        text_feedback = request.POST.get('comment')

        transaction = Transaction.objects.get(id=transactionid)

        if str(transaction.code) == str(code):
            transaction.timeliness = timeliness
            transaction.friendliness = friendliness
            transaction.responsetime = responsetime
            transaction.text_feedback = text_feedback[0:140]
            transaction.delivery_time = datetime.now()

            # Get item price, tip, quantity, and userwallet funds
            price = transaction.item.price
            tip = transaction.tip
            wallet = transaction.initiates.userprofile.wallet
            quantity = transaction.quantity

            # Do funds check again
            if tip + price*quantity > wallet:
               return render(request, 'menu/notenoughfunds.html')

            # Modify wallets
            transaction.delivers.userprofile.wallet += tip # Add tip to deliverer
            transaction.delivers.userprofile.save()

            transaction.initiates.userprofile.wallet -= tip + price*quantity # Subtract price and tip from requester
            transaction.initiates.userprofile.save()

            transaction.item.supplier.userprofile.wallet += price*quantity # Add price to supplier
            transaction.item.supplier.userprofile.save()
            
            # Save transaction and updated wallet in database
            transaction.save()
            # return success

            return render(request, "orders/exchangesuccess.html")
        else :
            # Wrong code message
            return render(request, "orders/wrongcode.html")
    else:
        # Error
        return render(request, "orders/error.html")

@user_passes_test(supplier_check, login_url='/notsupplier')
def telereport(request):

    context_dict={}
    userid = request.user.id

    # find transactions that have been completed
    transactions = Transaction.objects.filter(
        delivery_time__isnull=False)

    context_dict['transactions'] = transactions
    # render
    return render(request, "orders/telereport.html", context_dict)
