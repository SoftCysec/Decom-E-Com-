from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Category, Item, OrderItem, Order, Address
from django.utils import timezone
from django.contrib import messages
from django.views.generic import View, ListView
from django.core.mail import send_mail
from django.conf import settings
from .forms import CheckoutForm, CouponForm, ContactusForm
from django.db.models import Q
# Create your views here.
def categories(request):
    return {
        'categories': Category.objects.all()
    }


def item_list(request):
    search_product = request.GET.get('search')
    if search_product:
        products = Item.objects.filter(Q(title__icontains=search_product) & Q(slug__icontains=search_product, in_stock=True))
        return render(request, 'core/store.html', {'products': products})

    else:
        products = Item.objects.filter(in_stock=True)
        return render(request, 'core/store.html', {'products': products})


def product_detail(request, slug):
    product = get_object_or_404(Item, slug=slug, in_stock=True)
    context = {'product': product}
    return render(request, 'core/detail.html', context)

def category_list(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Item.objects.filter(category=category, in_stock=True)
    context = {'products': products, 'category': category}
    return render(request, 'core/category.html',  context)


def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:cart")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:cart")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:cart")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("core:cart")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:cart")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


#@login_required
class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user = self.request.user,ordered = False)
            context = {'object': order}
            return render(self.request, 'core/cart.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, 'You do not have an active order')
            return redirect("/")

class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {
            'form': form
        }
        return render(self.request, 'core/checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('shipping_address')
                apartment_address = form.cleaned_data.get('shipping_address2')
                country = form.cleaned_data.get('shipping_country')
                zip = form.cleaned_data.get('shipping_zip')
                same_billing_address = form.cleaned_data.get('same_billing_address')
                save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')

                checkout_address = Address(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip
                )
                checkout_address.save()
                order.checkout_address = checkout_address
                order.save()
                return redirect('core:checkout')
            messages.warning(self.request, "Failed Chekout")
            return redirect('core:checkout')

        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an order")
            return redirect("core:order-summary")

#seach
class SearchProduct(ListView):
    template_name = 'core/search.html'
    def get_queryset(self):
        val = self.kwargs.get("urlsearch")
        if val:
            products = Item.objects.filter(title__icontains=val)
        else:
            products = Item.objects.none()
        return products

def search_product(request):
    """ search function  """
    if request.method == "POST":
        query_name = request.POST.get('name', None)
        if query_name:
            products = Item.objects.filter(title__contains=query_name, in_stock=True)
            return render(request, 'core/search.html', {"products":products})

    return render(request, 'core/search.html')

def aboutus_view(request):
    return render(request,'core/aboutus.html')

def contactus_view(request):
    sub = ContactusForm()
    if request.method == 'POST':
        sub = ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message, settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'core/contactussuccess.html')
    return render(request, 'core/contactus.html', {'form':sub})

def cart(request):
    pass