from _pydecimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

from .models import *
from math import ceil
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.views.generic import View
from paypal.standard.forms import PayPalPaymentsForm

# Create your views here.
def first(request):
    ab = books.objects.filter(category='stationary')
    if request.method == 'POST':
        se = request.POST['search']
        if se:
            s = books.objects.filter(Q(name__icontains=se))
            if s:
                return render(request, "search.html", {"key": s})
            else:
                messages.error(request, "not found")
        else:
            return HttpResponseRedirect('search')
    return render(request, "first.html", {"ab": ab})


def contactview(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']
        a = contact(name=name, email=email, subject=subject, message=message)
        a.save()
    return render(request, "contact.html")


def sellerview(request):
    if request.method == "POST":
        sname = request.POST['sname']
        semail = request.POST['semail']
        snumber = request.POST['snumber']
        sstate = request.POST['sstate']
        s = seller(sname=sname, semail=semail, snumber=snumber, sstate=sstate)
        s.save()
    return render(request, "seller.html")


def login(request):
    if request.session.has_key('logged-in'):
        return render(request, '/')
    if request.method == 'POST':
        first = request.POST['username']
        second = request.POST['password']
        au = auth.authenticate(username=first, password=second)
        if au is not None:
            auth.login(request, au)
            request.session['logged-in'] = True
            return redirect('/')
        else:
            messages.error(request, "register first")
            return redirect('login')
    else:
        return render(request, "login.html")


def signup(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        rpassword = request.POST['rpassword']
        if (password == rpassword):
            if User.objects.filter(email=email).exists():
                messages.info(request, "check email")
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, "check username")
                return redirect('signup')
            else:
                ab = User.objects.create_user(first_name=first_name, username=username, email=email, password=password)
                ab.save()
                return render(request, "login.html")
        else:
            messages.info(request, "check password")
            return redirect('signup')
    else:
        return render(request, "signup.html")


def logout(request):
    auth.logout(request)
    return redirect('login')


def ug(request):
    allProds = []
    catprods = books.objects.values('subcategory', 'id')
    cats = {item['subcategory'] for item in catprods}
    for cat in cats:
        prod = books.objects.filter(subcategory=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    # params = {'no_of_slides':nSlides, 'range': range(1,nSlides),'product': products}
    # allProds = [[products, range(1, nSlides), nSlides],
    #             [products, range(1, nSlides), nSlides]]
    params = {'allProds': allProds}

    if request.method == 'POST':
        se = request.POST['search']
        if se:
            s = books.objects.filter(Q(name__icontains=se))
            if s:
                return render(request, "search.html", {"key": s})
            else:
                messages.error(request, "not found")
        else:
            return HttpResponseRedirect('search')

    return render(request, 'undergraduate.html', params)


def add_to_cart(request, slug):
    if request.session.has_key('logged-in'):
        item = get_object_or_404(books, slug=slug)
        order_item, created = Cart.objects.get_or_create(item=item, user=request.user)
        order_qs = Order.objects.filter(user=request.user)
        if order_qs.exists():
            order = order_qs[0]
            if order.orderitems.filter(item__slug=item.slug).exists():
                order_item.quantity += 1
                order_item.save()
                messages.info(request, "This item quantity was updated.")
                return redirect("undergraduate")
            else:
                order.orderitems.add(order_item)
                messages.info(request, "This item was added to your cart.")
                return redirect("undergraduate")
        else:
            order = Order.objects.create(user=request.user)
            order.orderitems.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("undergraduate")
    else:
        messages.warning(request, 'login first')
        return redirect('login')


# Remove item from cart
def remove_from_cart(request, slug):
    if request.session.has_key('logged-in'):
        item = get_object_or_404(books, slug=slug)
        cart_qs = Cart.objects.filter(user=request.user, item=item)
        if cart_qs.exists():
            cart = cart_qs[0]
            # Checking the cart quantity
            if cart.quantity > 1:
                cart.quantity -= 1
                cart.save()
            else:
                cart_qs.delete()
        order_qs = Order.objects.filter(user=request.user)
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.orderitems.filter(item__slug=item.slug).exists():
                order_item = Cart.objects.filter(
                    item=item,
                    user=request.user,
                )[0]
                order.orderitems.remove(order_item)
                messages.info(request, "This item was removed from your cart.")
                return redirect("undergraduate")
            else:
                messages.info(request, "This item was not in your cart")
                return redirect("undergraduate")
        else:
            messages.info(request, "You do not have an active order")
            return redirect("undergraduate")
    else:
        messages.warning(request, 'login first')
        return redirect('login')


class order_summary(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


def search(request):
    return render(request, 'search.html')


def address(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        street1 = request.POST['street1']
        street2 = request.POST['street2']
        city = request.POST['city']
        state = request.POST['state']
        num = request.POST['num']
        pin = request.POST['pin']
        sav = address(full_name=full_name, street1=street1, street2=street2, city=city, state=state, num=num, pin=pin)
        sav.save()
    return render(request, 'address.html')


def remove_single_item_from_cart(request, slug):
    if request.session.has_key('logged-in'):
        item = get_object_or_404(books, slug=slug)
        cart_qs = Cart.objects.filter(user=request.user, item=item)
        if cart_qs.exists():
            cart = cart_qs[0]
            # Checking the cart quantity
            if cart.quantity > 1:
                cart.quantity -= 1
                cart.save()
            else:
                cart_qs.delete()
        order_qs = Order.objects.filter(user=request.user)
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.orderitems.filter(item__slug=item.slug).exists():
                order_item = Cart.objects.filter(
                    item=item,
                    user=request.user,
                )[0]
                order.orderitems.remove(order_item)
                messages.info(request, "This item was removed from your cart.")
                return redirect("order_summary")
            else:
                messages.info(request, "This item was not in your cart")
                return redirect("order_summary")
        else:
            messages.info(request, "You do not have an active order")
            return redirect("order_summary")
    else:
        messages.warning(request, 'login first')
        return redirect('login')


def payment(request):
    return render(request, "payment.html")


def process_payment(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    host = request.get_host()

    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': '%.2f' % order.total_cost().quantize(
            Decimal('.01')),
        'item_name': 'Order {}'.format(order.id),
        'invoice': str(order.id),
        'currency_code': 'USD',
        'notify_url': 'http://{}{}'.format(host,
                                           reverse('paypal-ipn')),
        'return_url': 'http://{}{}'.format(host,
                                           reverse('payment_done')),
        'cancel_return': 'http://{}{}'.format(host,
                                              reverse('payment_cancelled')),
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'payment', {'order': order, 'form': form})

def payment_success(request):
    return render(request,"success_payment.html")