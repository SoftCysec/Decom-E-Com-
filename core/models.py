from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django_countries.fields import CountryField
# Create your models here.
CATEGORY_CHOICES = (
    ('FD', 'Food'),
    ('CL', 'Clothes'),
    ('Sh', 'Shoes'),
)

class Category(models.Model):
    name = models.CharField(max_length=50, db_index=True, blank=True, null=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse("core:category_list", args=[self.slug])


    def __str__(self):
        return self.name

class Item(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    category = models.ForeignKey("Category", related_name='product', on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(null=True, blank=True)
    slug = models.SlugField(max_length=50, blank=True, null=True)
    in_stock = models.BooleanField(default=True, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)
    

    class Meta:
        verbose_name_plural = 'Products'
        ordering = ('-created',)

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    def get_absolute_url(self):
        return reverse('core:product_detail', args=[self.slug])

    def get_add_to_cart_url(self):
         return reverse('core:add-to-cart', kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
            return reverse('core:remove-from-cart', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_price(self):
        return self.quantity * self.item.price


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_total_price()
        return total

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

class Address(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE, blank=True, null=True)
    street_address = models.CharField(max_length=100, blank=True, null=True)
    apartment_address = models.CharField(max_length=100, blank=True, null=True)
    country = CountryField(multiple=False, blank=True, null=True)
    zip = models.CharField(max_length=100, blank=True, null=True)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES,blank=True, null=True)
    default = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50, blank=True, null=True)
    user = models.ForeignKey(User,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15, blank=True, null=True)
    amount = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.code