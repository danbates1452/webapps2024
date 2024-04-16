from django.contrib import admin
from .models import Person, Transaction, Request


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("user", "active", "balance")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("from_person", "to_person", "amount", "submission_datetime")


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ("by_person", "to_person", "amount", "status")
