from django.contrib import admin
from .models import Person, Transaction, Request

admin.site.register(Person)
admin.site.register(Transaction)
admin.site.register(Request)
