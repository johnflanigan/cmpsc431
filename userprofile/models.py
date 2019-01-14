from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# User Profile model
class UserProfile(models.Model):

    # link user profile to a user
    user = models.OneToOneField(User)

    # profile fields
    supplier_flag = models.BooleanField(default=False)
    location = models.CharField(max_length=128)
    phone_number = models.BigIntegerField(validators=[MaxValueValidator(9999999999)])
    wallet = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self):
        return self.user.username

    def __unicode__(self):
        return self.user.username


# Payment Model
class Payment(models.Model):

    # Links Payment to User
    user = models.OneToOneField(User)

    # credit card information
    creditcard_number = models.CharField(max_length=16)
    security_code = models.CharField(max_length=3)
    expiration_month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    expiration_year = models.IntegerField(
        validators=[MinValueValidator(00), MaxValueValidator(99)]
    )

    def __str__(self):
        return self.user.username

    def __unicode__(self):
        return self.user.username


# Levels model
class Levels(models.Model):
    number_transactions = models.IntegerField()
    level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )

    def __str__(self):
        return self.number_transactions

    def __unicode__(self):
        return self.number_transactions
