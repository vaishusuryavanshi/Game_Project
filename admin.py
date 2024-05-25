from django.contrib import admin
from gameapp.models import Product

# Register your models here.

class productAdmin(admin.ModelAdmin):
    list_display = ['id','productName','description','manufacturer','cat','is_available','price','image']


admin.site.register(Product,productAdmin)
