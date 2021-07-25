from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .forms import RegistrationForm, LoginForm, ProductForm, GalleryForm, CheckoutForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.utils.text import slugify
from .models import Product, Gallery, Cart, CartItem, OrderItem, Order
from django.forms.models import model_to_dict
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import stripe
stripe.api_key = 'sk_test_51HwxtWKGMCME6NPHfighliPklMhtKqB5EIGyHfl39STqOUZiaRCeu1PAsZTg0vtfguqbAuJn7wl89mHv5QCGaI1p00mSYEV3Xv'


# Create your views here.
def index(request):
    products = Product.objects.all()
    return render(request, 'shopline/pages/home.html', {
        'products': products
    })


def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            buyer = Group.objects.get(name='buyer')
            user.groups.add(buyer)
            login(request, user)
            return HttpResponseRedirect(reverse('shopline:dashboard'))

        return render(request, 'shopline/registration.html', {
            'form': form
        })
    else:
        form = RegistrationForm()

        return render(request, 'shopline/registration.html', {
            'form': form
        })


def dashboard(request):
    return render(request, 'shopline/dashboard.html')


def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('shopline:dashboard'))
            else:
                messages.warning(request, 'Username or password is wrong')
                return HttpResponseRedirect(reverse('shopline:login_user'))

        return render(request, 'shopline/login.html', {
            'form': form
        })
    else:
        form = LoginForm()

        return render(request, 'shopline/login.html', {
            'form': form
        })


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('shopline:index'))


def register_merchant(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            seller = Group.objects.get(name='seller')
            user.groups.add(seller)
            login(request, user)
            return HttpResponseRedirect(reverse('shopline:dashboard'))

        return render(request, 'shopline/register-merchant.html', {
            'form': form
        })
    else:
        form = RegistrationForm()

        return render(request, 'shopline/register-merchant.html', {
            'form': form
        })


def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES or None)
        if form.is_valid():
            product = form.save(commit=False)
            product.user_id = request.user.id
            product.slug = slugify(product.title)
            product.save()
            messages.success(request, 'Product:added')
            return HttpResponseRedirect(reverse('shopline:dashboard_products'))

        return render(request, 'shopline/product/create.html', {
            'form': form
        })
    else:
        form = ProductForm()

        return render(request, 'shopline/product/create.html', {
            'form': form
        })


def dashboard_products(request):
    products = Product.objects.filter(user=request.user)

    return render(request, 'shopline/dashboard/products.html', {
        'products': products
    })


def product_edit(request, id):
    product = Product.objects.get(pk=id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES or None, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.user_id = request.user.id
            product.slug = slugify(product.title)
            product.save()
            messages.success(request, 'Product:added')
            return HttpResponseRedirect(reverse('shopline:dashboard_products'))

        return render(request, 'shopline/product/edit.html', {
            'form': form,
            'product': product
        })
    else:
        form = ProductForm(initial=model_to_dict(product))

        return render(request, 'shopline/product/edit.html', {
            'form': form,
            'product': product
        })


def product_delete(request, id):
    product = Product.objects.get(pk=id)
    product.delete()
    messages.success(request,'Product removed successfully')
    return HttpResponseRedirect(reverse('shopline:dashboard_products'))


def product_gallery(request, id):
    product = Product.objects.get(pk=id)
    gallery = product.gallery.all()

    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES or None)
        if form.is_valid():
            files = request.FILES.getlist('image')

            for f in files:
                gallery = Gallery(image=f, product=product)
                gallery.save()

            messages.success(request, 'Product gallery updated')
            return HttpResponseRedirect(reverse('shopline:product_gallery', args=(product.id,)))
        return render(request, 'shopline/product/gallery.html', {
            'product': product,
            'form': form,
            'gallery': gallery
        })
    else:
        form = GalleryForm()

        return render(request, 'shopline/product/gallery.html', {
            'product': product,
            'gallery': gallery,
            'form': form,
        })


def product_gallery_delete(request, id):
    image = Gallery.objects.get(pk=id)
    product = image.product.id
    image.delete()
    messages.success(request,'Gallery image removed')
    return HttpResponseRedirect(reverse('shopline:product_gallery', args=(product,)))


def product_show(request, slug):
    product = Product.objects.get(slug=slug)

    return render(request, 'shopline/product/show.html', {
        'product': product
    })


def add_cart_item(request):
    if request.method == 'POST':
        product = Product.objects.get(pk=request.POST['product_id'])
        quantity = int(request.POST['quantity'])
        try:
            cart = Cart.objects.get(user=request.user)
            cart.total = cart.total + (product.price * quantity)
            cart.save()
        except Cart.DoesNotExist:
            cart = Cart(user=request.user)
            cart.total = product.price * quantity
            cart.save()

        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=quantity
        )

        messages.success(request, 'Product added to cart')
        return HttpResponseRedirect(reverse('shopline:cart'))


def cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart = cart.objects.create(user=request.user)

    return render(request, 'shopline/pages/cart.html', {
        'cart': cart
    })


def delete_cart_item(request, id):
    if request.method == 'POST':
        item = CartItem.objects.get(pk=id)
        cart = Cart.objects.get(pk=item.cart.id)
        cart.total = cart.total - (item.product.price * item.quantity)
        cart.save()
        item.delete()
        messages.success(request, 'Product removed from cart')
        return HttpResponseRedirect(reverse('shopline:cart'))


def order(request):
    cart = Cart.objects.get(user=request.user)
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.status = 'created'
            order.created_at = datetime.now()
            order.updated_at = datetime.now()
            order.total = cart.total
            order.save()

            #set order items
            for item in cart.cart_item.all():
                OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

            return HttpResponseRedirect(reverse('shopline:checkout'))

        return render(request, 'shopline/pages/order.html', {
           'cart': cart,
           'form': form
        })
    else:
        form = CheckoutForm()

        return render(request, 'shopline/pages/order.html', {
            'cart': cart,
            'form': form
        })


@csrf_exempt
def checkout(request):
    if request.method == 'POST':
        order = Order.objects.filter(user=request.user, status='created').order_by('created_at').first()
        cart = Cart.objects.get(user=request.user)
        try:
            domain_url = 'http://127.0.0.1:8000/'
            session = stripe.checkout.Session.create(
                success_url=domain_url + 'shopline/payment/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'shopline/payment/cancelled',
                payment_method_types=['card'],
                mode='payment',
                line_items=get_order_items(order)
            )
            #order data update karna idhar
            order.session_id = session.id
            order.payment_id = session.payment_intent
            order.save()

            #Uske baad cart items remove karna
            cart.total = 0
            cart.cart_items.all().delete()
            cart.save()

            return JsonResponse({"sessionId": session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e), "hello": "satyam"})


    else:
        return render(request, 'shopline/pages/checkout.html')


def get_order_items(order):
    items = []
    print('order', order)
    for item in order.order_item.all():
        items.append({
            'price_data': {
                'currency': 'inr',
                'unit_amount': item.product.price * 100,
                'product_data': {
                    'name': item.product.title
                }
            },
        })
    return items

