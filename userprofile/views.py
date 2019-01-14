from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from userprofile.forms import UserForm, UserProfileForm, PaymentForm
from userprofile.models import UserProfile, Payment
from django.core.exceptions import ObjectDoesNotExist
from orders.models import Transaction
from django.db.models import Q
from django.contrib.auth.models import User
from decimal import Decimal


# registration view
def register(request):

    # create flag for successful registration
    registered = False

    # if submitted, process form
    if request.method == 'POST':

        # grab information from forms
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        payment_form = PaymentForm(data=request.POST)

        # if those are valid, continue
        if user_form.is_valid() and profile_form.is_valid() and payment_form.is_valid():

            # save user form to database
            user = user_form.save()

            # hash password and send to user object
            user.set_password(user.password)

            # save user
            user.save()

            # prepare userprofile form
            profile = profile_form.save(commit=False)

            # connect userprofile with user
            profile.user = user

            # save userprofile
            profile.save()

            # Do same thing for payment as profile
            payment = payment_form.save(commit=False)
            payment.user = user
            payment.save()

            # flag successful registration
            registered = True

        # else forms invalid, print errors
        else:
            print(user_form.errors, profile_form.errors)

    # else show the registration form
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
        payment_form = PaymentForm()

    # Render the template depending on the context.
    return render(request, 'userprofile/register.html',
                      {'user_form': user_form,
                       'profile_form': profile_form,
                       'payment_form': payment_form,
                       'registered': registered})


# login view
def user_login(request):

    # if submitted, process form
    if request.method == 'POST':

        # get username and password
        username = request.POST.get('username')
        password = request.POST.get('password')

        # authenticate: if successful, user object returned
        user = authenticate(username=username,password=password)

        # if successful authentication
        if user:

            # check if active
            if user.is_active:

                # login and return to homepage
                login(request, user)
                return HttpResponseRedirect(reverse('index'))

            # else return error page
            else:
                return HttpResponse("Your account is disabled. Please contact the system administrator.")

        # else bad login details, return error page
        else:
            print("Invalid authentication details.")
            return render(request, 'userprofile/invalidlogin.html')

    # else render login form
    else:
        return render(request, 'userprofile/login.html', {})


# logout view
@login_required
def user_logout(request):

    # logout user
    logout(request)

    # Take the user back to the hompage
    return render(request, 'userprofile/logout.html')


# view profile view
@login_required
def view_my_profile(request):

    # get user information
    user = request.user
    userid = request.user.id
    userprofile = UserProfile.objects.get(
        user_id=userid
    )
    
    try:
        payment = Payment.objects.get(
            user_id=userid
        )
    except ObjectDoesNotExist:
        payment = None

    requests = Transaction.objects.filter(
        initiates__exact=userid).filter(
        delivery_time__isnull=False)

    deliveries = Transaction.objects.filter(
        delivers=userid).filter(
        delivery_time__isnull=False)

    # Count user level
    numtransactions = Transaction.objects.filter(
        Q(initiates__exact=userid)|Q(delivers=userid)).count()
    level = (numtransactions / 5) + 1

    # pass to context dict
    context_dict = {'user' : user,
                    'userprofile' : userprofile,
                    'level' : level,
                    'payment' : payment,
                    'requests' : requests,
                    'deliveries' : deliveries}

    # render
    return render(request, 'userprofile/viewmyprofile.html', context_dict)

def view_other_profile(request):

    if request.method == 'GET':

        username = request.GET['username']
        user = User.objects.get(username=username)

        numtransactions = Transaction.objects.filter(
            Q(initiates__exact=user.id)|Q(delivers=user.id)).count()
        level = (numtransactions / 5) + 1

        context_dict = {'user' : user,
                        'userprofile' : user.userprofile,
                        'level' : level}

        return render(request, 'userprofile/viewotherprofile.html', context_dict)

    else:
        return HttpResponse('An error occured. Please return to homepage')

@login_required
def addfunds(request):
    if request.method == 'GET':
        return render(request, "userprofile/addfunds.html")
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount'))

        userid = request.user.id
        userprofile = UserProfile.objects.get(
            user_id=userid
        )

        userprofile.wallet += amount
        userprofile.save()

        return render(request, "userprofile/fundsadded.html")



