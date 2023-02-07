from django.contrib import admin
from .models import Item, OrderItem, Order, Category, Address, Payment
# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Item)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'slug', 'price', 'in_stock', 'created', 'updated'
    ]
    list_filter = ['in_stock', 'is_active']
    list_editable = ['price', 'in_stock']
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Address)
admin.site.register(Payment)