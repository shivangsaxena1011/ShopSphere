import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.db.models import Q

from store.models import Product, Category, Order, OrderItem, UserProfile
from store.cart import Cart
from store.forms import UserRegisterForm, UserLoginForm, CheckoutForm, UserProfileForm
from store.services import create_order_from_cart


def home_view(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    if not featured_products.exists():
        featured_products = Product.objects.filter(is_active=True)[:8]

    latest_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    categories = Category.objects.filter(is_active=True).order_by('name')

    context = {
        'featured_products': featured_products,
        'latest_products': latest_products,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)


def product_list_view(request):
    category_slug = request.GET.get('category')
    query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', 'featured')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    products = Product.objects.filter(is_active=True)
    selected_category = None

    if category_slug and category_slug != 'all':
        selected_category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=selected_category)

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    if min_price:
        try:
            products = products.filter(price__gte=Decimal(min_price))
        except (ValueError, TypeError):
            pass

    if max_price:
        try:
            products = products.filter(price__lte=Decimal(max_price))
        except (ValueError, TypeError):
            pass

    # Sorting
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else:  # featured or default
        products = products.order_by('-is_featured', '-created_at')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(is_active=True).order_by('name')

    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'categories': categories,
        'selected_category': selected_category,
        'current_category_slug': category_slug or 'all',
        'query': query,
        'sort_by': sort_by,
        'min_price': min_price or '',
        'max_price': max_price or '',
        'total_count': paginator.count,
    }
    return render(request, 'store/product_list.html', context)


def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
        'specs_list': product.get_specs_list(),
    }
    return render(request, 'store/product_detail.html', context)


def cart_view(request):
    cart = Cart(request)
    context = {
        'cart': cart,
        'subtotal': cart.get_subtotal(),
        'shipping': cart.get_shipping_cost(),
        'total': cart.get_total(),
    }
    return render(request, 'store/cart.html', context)


@require_POST
def cart_add_view(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    if not product.in_stock:
        messages.error(request, f"Sorry, '{product.name}' is out of stock.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Product is out of stock.'}, status=400)
        return redirect(request.META.get('HTTP_REFERER', 'cart'))

    cart.add(product=product, quantity=quantity)
    messages.success(request, f"Added {product.name} to your shopping cart!")

    # Check if Buy Now was pressed
    if request.POST.get('buy_now') == '1':
        return redirect('checkout')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'cart_count': len(cart),
            'cart_total': str(cart.get_total()),
            'message': f"Added {product.name} to your cart!"
        })

    return redirect(request.META.get('HTTP_REFERER', 'cart'))


@require_POST
def cart_update_view(request):
    cart = Cart(request)
    product_id = request.POST.get('product_id')
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    if not product_id:
        return HttpResponseBadRequest("Missing product_id")

    product = get_object_or_404(Product, id=product_id)
    cart.update(product=product, quantity=quantity)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        item_line_total = Decimal('0.00')
        for item in cart:
            if item['product'].id == product.id:
                item_line_total = item['line_total']
                break

        return JsonResponse({
            'status': 'success',
            'cart_count': len(cart),
            'line_total': f"₹{item_line_total:,.2f}",
            'subtotal': f"₹{cart.get_subtotal():,.2f}",
            'total': f"₹{cart.get_total():,.2f}",
        })

    return redirect('cart')


@require_POST
def cart_remove_view(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f"Removed {product.name} from your cart.")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'cart_count': len(cart),
            'subtotal': f"₹{cart.get_subtotal():,.2f}",
            'total': f"₹{cart.get_total():,.2f}",
        })

    return redirect('cart')


@login_required
def checkout_view(request):
    cart = Cart(request)

    if len(cart) == 0:
        messages.warning(request, "Your cart is empty. Please add items before checking out.")
        return redirect('product_list')

    profile = getattr(request.user, 'profile', None)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                order = create_order_from_cart(request.user, cart, form.cleaned_data)
                messages.success(request, f"Your order #{order.order_number} has been placed successfully!")
                return redirect('order_success', order_number=order.order_number)
            except ValidationError as e:
                messages.error(request, str(e.message if hasattr(e, 'message') else e))
            except Exception as e:
                messages.error(request, f"An unexpected error occurred while placing your order: {e}")
    else:
        # Initial prefill from profile
        initial_data = {
            'full_name': request.user.get_full_name() or request.user.username,
            'phone': profile.phone if profile else '',
            'address': profile.address if profile else '',
            'city': profile.city if profile else '',
            'state': profile.state if profile else '',
            'postal_code': profile.postal_code if profile else '',
        }
        form = CheckoutForm(initial=initial_data)

    context = {
        'form': form,
        'cart': cart,
        'subtotal': cart.get_subtotal(),
        'shipping': cart.get_shipping_cost(),
        'total': cart.get_total(),
    }
    return render(request, 'store/checkout.html', context)


@login_required
def order_success_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'store/order_success.html', {'order': order})


@login_required
def order_history_view(request):
    status_filter = request.GET.get('status', 'all').capitalize()

    orders_qs = Order.objects.filter(user=request.user).prefetch_related('items__product')

    if status_filter in ['Placed', 'Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']:
        if status_filter == 'Pending':
            orders_qs = orders_qs.filter(Q(status='Placed') | Q(payment_status='Pending'))
        else:
            orders_qs = orders_qs.filter(status=status_filter)

    total_orders_count = Order.objects.filter(user=request.user).count()
    active_cod_total = sum(
        o.total for o in Order.objects.filter(user=request.user).exclude(status__in=['Delivered', 'Cancelled'])
    )
    delivered_count = Order.objects.filter(user=request.user, status='Delivered').count()

    context = {
        'orders': orders_qs,
        'current_status': request.GET.get('status', 'all'),
        'total_orders_count': total_orders_count,
        'active_cod_total': active_cod_total,
        'delivered_count': delivered_count,
    }
    return render(request, 'store/order_history.html', context)


@login_required
def order_detail_view(request, order_number):
    # Enforce IDOR protection: only the owner can view this order
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


def user_register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            full_name = form.cleaned_data['full_name']

            username = email.split('@')[0]
            # Ensure unique username
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            first_name = full_name.split()[0] if full_name else ''
            last_name = " ".join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Auto-login after registration
            login(request, user)
            cart = Cart(request)
            cart.merge_from_db_to_session(user)

            messages.success(request, f"Welcome to ShopSphere, {full_name or username}! Your account has been created.")
            return redirect('home')
    else:
        form = UserRegisterForm()

    return render(request, 'registration/register.html', {'form': form})


def user_login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)

            # Support login with either username or email
            user = None
            if '@' in username_or_email:
                user_obj = User.objects.filter(email__iexact=username_or_email).first()
                if user_obj:
                    user = authenticate(request, username=user_obj.username, password=password)
            else:
                user = authenticate(request, username=username_or_email, password=password)

            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)  # Session closes on browser close

                # Merge session cart with database cart
                cart = Cart(request)
                cart.merge_from_db_to_session(user)

                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('home')
            else:
                messages.error(request, "Invalid email/username or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'registration/login.html', {'form': form})


@login_required
def user_logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out securely. See you soon!")
    return redirect('home')


@login_required
def user_profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save()
            user = request.user
            user.first_name = form.cleaned_data.get('first_name', user.first_name)
            user.last_name = form.cleaned_data.get('last_name', user.last_name)
            user.email = form.cleaned_data.get('email', user.email)
            user.save()
            messages.success(request, "Your profile details have been updated successfully.")
            return redirect('user_profile')
    else:
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        form = UserProfileForm(instance=profile, initial=initial_data)

    orders_count = Order.objects.filter(user=request.user).count()
    context = {
        'form': form,
        'profile': profile,
        'orders_count': orders_count,
    }
    return render(request, 'store/profile.html', context)


# Custom error handlers
def custom_permission_denied_view(request, exception=None):
    return render(request, 'errors/403.html', status=403)

def custom_page_not_found_view(request, exception=None):
    return render(request, 'errors/404.html', status=404)

def custom_server_error_view(request):
    return render(request, 'errors/500.html', status=500)
