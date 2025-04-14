import random
import logging
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from .forms import RegForm, LoginForm, ProfileForm, CheckoutForm, OTPForm
from .models import Account, Product, ProductImage, Order, OrderItem, CATEGORY_CHOICES


logger = logging.getLogger(__name__)

# --- Registration View ---
def reg(request):
    """Handles user registration form display (GET) and submission (POST)."""
    if request.user.is_authenticated:
        return redirect('app1:home')

    if request.method == 'POST':
        form = RegForm(request.POST)
        if form.is_valid():
            signup_data = form.cleaned_data.copy()
            password = signup_data.pop('password', None)
            signup_data.pop('confirm_password', None)

            if not password:
                messages.error(request, 'Password missing during registration process.')
                return render(request, 'reg.html', {'form': form})

            request.session['signup_data'] = signup_data
            request.session['signup_password'] = password

            otp = random.randint(100000, 999999)
            request.session['signup_otp'] = otp

            logger.info(f"Generated OTP {otp} for {signup_data['email']}")
            print(f"Generated OTP for {signup_data['email']}: {otp}")

            subject = 'Your Account Verification OTP'
            message = f'Your OTP for registration is: {otp}\n\nThis OTP is valid for 5 minutes.'
            from_email = settings.DEFAULT_FROM_EMAIL or 'webmaster@localhost'
            recipient_list = [signup_data['email']]

            try:
                print(f"Trying to send mail to {recipient_list} from {from_email}...")
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                print("Mail sent successfully")

                messages.info(request, 'Registration details received. Please check your email (or console) for the OTP.')
                return redirect('app1:verify_otp')

            except Exception as e:
                logger.error(f"Failed to send OTP email to {signup_data['email']}: {e}", exc_info=True)
                messages.error(request, f'Failed to send OTP: {e}. Please try registering again.')
                request.session.pop('signup_data', None)
                request.session.pop('signup_otp', None)
                request.session.pop('signup_password', None)
        else:
            messages.error(request, 'Please correct the errors below.')

    form = RegForm() if request.method == 'GET' else form
    return render(request, 'reg.html', {'form': form})


# --- OTP Verification ---
def verify_otp(request):
    """Handles OTP form display (GET) and verification (POST)."""
    signup_data = request.session.get('signup_data')
    stored_otp = request.session.get('signup_otp')
    password = request.session.get('signup_password')

    if not all([signup_data, stored_otp, password]):
         if request.method == 'POST':
              messages.error(request, 'Registration session data is missing or expired. Please register again.')
              for key in ['signup_data', 'signup_otp', 'signup_password']: request.session.pop(key, None)
              return redirect('app1:reg')
         elif 'signup_data' not in request.session or 'signup_otp' not in request.session:
              messages.error(request, 'No pending registration found or session expired. Please register again.')
              return redirect('app1:reg')

    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            submitted_otp = form.cleaned_data['otp']
            if str(submitted_otp) == str(stored_otp):
                try:
                    hashed_password = make_password(password)
                    user = Account.objects.create(
                        password=hashed_password,
                        **signup_data
                    )
                    for key in ['signup_data', 'signup_otp', 'signup_password']:
                        request.session.pop(key, None)

                    login(request, user)
                    messages.success(request, 'Account verified and created successfully! You are now logged in.')
                    return redirect('app1:home')

                except IntegrityError:
                    messages.error(request, 'An account with this username or email already exists. Please try logging in or use a different username/email.')
                    for key in ['signup_data', 'signup_otp', 'signup_password']: request.session.pop(key, None)
                    return redirect('app1:reg')
                except Exception as e:
                    logger.error(f"Unexpected error creating account for {signup_data.get('email')}: {e}", exc_info=True)
                    messages.error(request, f'Failed to create account due to an unexpected error. Please try again.')
                    for key in ['signup_data', 'signup_otp', 'signup_password']: request.session.pop(key, None)
                    return redirect('app1:reg')
            else:
                messages.error(request, 'Invalid OTP entered. Please try again.')
        else:
            messages.error(request, 'Please enter the 6-digit OTP.')

    form = OTPForm() if request.method == 'GET' else form
    email_display = request.session.get('signup_data', {}).get('email', 'your email address')
    context = {
        'form': form,
        'email': email_display
    }
    return render(request, 'verify_otp.html', context)

def login_view(request):
    """Handles user login."""
    if request.user.is_authenticated:
       return redirect('app1:home')
    form = LoginForm(request.POST or None)
    unmatch = ''
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next')
                if next_url and not next_url.startswith('//') and not next_url.startswith('http://') and not next_url.startswith('https://'):
                    return redirect(next_url)
                else:
                    return redirect('app1:home')
            else:
                unmatch = "Username or password didn't match."
        else:
             unmatch = "Invalid login details provided."
    return render(request, 'login.html', {'form': form, 'data': unmatch})


def logout_view(request):
    """Logs the user out."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('app1:home')

def home_view(request):
    """Displays home page with featured products by category."""
    laptops = Product.objects.filter(category='laptop', stock__gt=0).order_by('-created_at')[:4]
    prebuilts = Product.objects.filter(category='prebuilt', stock__gt=0).order_by('-created_at')[:4]
    parts = Product.objects.filter(category='part', stock__gt=0).order_by('-created_at')[:4]
    context = {
        'data': request.user,
        'laptops': laptops,
        'prebuilts': prebuilts,
        'parts': parts,
    }
    return render(request, 'home.html', context)

@login_required(login_url='app1:login')
def profile_view(request):
    """Displays and handles profile updates."""
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('app1:profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileForm(instance=user)
    return render(request, 'profile.html', {'form': form, 'user': user})

def product_detail(request, pk):
    """Displays details for a single product."""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product, 'user': request.user}) # Pass user

def search_view(request):
    """Handles product search."""
    query = request.GET.get('q', '')
    results = []
    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).order_by('-created_at')
    context = {
        'query': query,
        'results': results,
        'result_count': results.count() if results else 0,
        'user': request.user
    }
    return render(request, 'search_results.html', context)

@login_required(login_url='app1:login')
def add_to_cart(request, product_id):
    """Adds a product to the cart via AJAX - REQUIRES LOGIN."""
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Product not found.'}, status=404)

    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    current_quantity_in_cart = cart.get(product_id_str, {}).get('quantity', 0)
    if product.stock <= current_quantity_in_cart:
        return JsonResponse({'status': 'error', 'message': f"'{product.name}' is out of stock or quantity limit reached."}, status=400)

    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1
    else:
        cart[product_id_str] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': 1,
            'image': product.images.first().image.url if product.images.exists() and product.images.first().image else None,
        }

    request.session['cart'] = cart
    cart_count = sum(item['quantity'] for item in cart.values())

    return JsonResponse({
        'status': 'success',
        'message': f"Added '{product.name}' to cart!",
        'cart_count': cart_count
    })


@login_required(login_url='app1:login')
def cart_view(request):
    """Displays the shopping cart page."""
    cart = request.session.get('cart', {})
    cart_items_detailed = []
    total_price = 0
    for product_id, item in cart.items():
        try:
            item_price = float(item['price'])
            item_quantity = int(item['quantity'])
            item_total = item_price * item_quantity
            total_price += item_total
            cart_items_detailed.append({
                'product_id': product_id,
                'name': item['name'],
                'price': item_price,
                'quantity': item_quantity,
                'image': item.get('image'),
                'subtotal': item_total,
            })
        except (ValueError, TypeError):
            messages.error(request, f"Invalid item data in cart for product ID {product_id}. Please remove and re-add.")
            pass

    return render(request, 'cart.html', {'cart_items': cart_items_detailed, 'total_price': total_price})


@login_required(login_url='app1:login')
def update_cart(request, product_id):
    """Updates item quantity in the cart."""
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str not in cart:
        messages.error(request, "Item not found in cart.")
        return redirect('app1:cart')

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                item_name = cart[product_id_str].get('name', 'Item')
                del cart[product_id_str]
                messages.info(request, f"Removed '{item_name}' from cart.")
            else:
                product = get_object_or_404(Product, id=product_id)
                if product.stock < quantity:
                    messages.warning(request, f"Sorry, only {product.stock} units available for '{product.name}'. Quantity not updated.")
                else:
                    cart[product_id_str]['quantity'] = quantity
                    messages.success(request, f"Updated quantity for '{product.name}'.")

            request.session['cart'] = cart
        except ValueError:
            messages.error(request, "Invalid quantity specified.")
        except Product.DoesNotExist:
             messages.error(request, "Product associated with cart item not found.") # Handle product gone

    return redirect('app1:cart')

@login_required(login_url='app1:login')
def remove_from_cart(request, product_id):
    """Removes an item from the cart."""
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    if product_id_str in cart:
        item_name = cart[product_id_str].get('name', 'Item')
        del cart[product_id_str]
        request.session['cart'] = cart
        messages.info(request, f"Removed '{item_name}' from cart.")
    else:
        messages.error(request, "Item not found in cart.")
    return redirect('app1:cart')


@login_required(login_url='app1:login')
def checkout_view(request):
    """Handles checkout: address form, order creation, stock update, email."""
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect('app1:home')

    total_amount = 0
    items_for_order = []
    can_proceed = True
    for product_id, item_data in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            item_quantity = int(item_data['quantity'])
            item_price = float(item_data['price'])

            if product.stock < item_quantity:
                messages.error(request, f"Sorry, '{product.name}' has insufficient stock ({product.stock} available). Please update your cart.")
                can_proceed = False

            item_total = item_price * item_quantity
            total_amount += item_total
            items_for_order.append({
                'product': product,
                'quantity': item_quantity,
                'price': item_price
            })
        except Product.DoesNotExist:
             messages.error(request, f"Product with ID {product_id} not found. Please remove it from cart.")
             can_proceed = False
        except (ValueError, TypeError) as e:
             messages.error(request, f"Invalid data for product ID {product_id} in cart ({e}). Please remove and re-add.")
             can_proceed = False

    if not can_proceed:
        return redirect('app1:cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            shipping_address = form.cleaned_data['shipping_address']
            billing_address = form.cleaned_data.get('billing_address') or shipping_address

            try:
                with transaction.atomic():
                    order = Order.objects.create(
                        user=request.user, total_amount=total_amount,
                        shipping_address=shipping_address, billing_address=billing_address,
                        order_status='processing'
                    )

                    for item in items_for_order:
                        OrderItem.objects.create(
                            order=order, product=item['product'],
                            quantity=item['quantity'], price=item['price']
                        )

                    for item_data in items_for_order:
                        product_to_update = Product.objects.select_for_update().get(id=item_data['product'].id)
                        if product_to_update.stock >= item_data['quantity']:
                            product_to_update.stock -= item_data['quantity']
                            product_to_update.save()
                        else:
                            raise IntegrityError(f"Insufficient stock for {product_to_update.name} during final processing.")

                try:
                    subject = f'Your Order #{order.id} is Confirmed!'
                    message = (
                        f"Hi {order.user.username},\n\n"
                        f"Your order #{order.id} for ₹{order.total_amount:.2f} has been confirmed and is being processed.\n\n"
                        f"Shipping Address:\n{order.shipping_address}\n\n"
                        f"You can view your order details here: {request.build_absolute_uri(reverse('app1:order_detail', args=[order.id]))}\n\n"
                        f"Thank you for shopping with us!"
                    )
                    from_email = settings.DEFAULT_FROM_EMAIL
                    recipient_list = [order.user.email]
                    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                except Exception as mail_error:
                     logger.error(f"Order {order.id} placed, but failed to send confirmation email to {order.user.email}: {mail_error}", exc_info=True)
                     messages.warning(request, f"Order #{order.id} confirmed successfully, but there was an issue sending the confirmation email.")
                else:
                     messages.success(request, f"Order #{order.id} confirmed successfully! A confirmation email has been sent.")

                request.session.pop('cart', None)
                return redirect('app1:order_history')

            except IntegrityError as e:
                 messages.error(request, f"Could not complete order due to stock issue: {e}")
                 return render(request, 'checkout.html', {'cart': cart, 'total_amount': total_amount, 'form': form})
            except Exception as e:
                logger.error(f"Unexpected error during checkout for user {request.user.id}: {e}", exc_info=True)
                messages.error(request, f"An unexpected error occurred: {e}. Please try again.")
                return render(request, 'checkout.html', {'cart': cart, 'total_amount': total_amount, 'form': form})
        else:
            messages.error(request, "Please correct the errors in the address form.")
            context = {'cart': cart, 'total_amount': total_amount, 'form': form}
            return render(request, 'checkout.html', context)
    else:
        form = CheckoutForm()
        context = {'cart': cart, 'total_amount': total_amount, 'form': form}
        return render(request, 'checkout.html', context)

@login_required(login_url='app1:login')
def order_history_view(request):
    """Displays the user's order history."""
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'order_history.html', {'orders': orders})

@login_required(login_url='app1:login')
def order_detail_view(request, order_id):
    """Displays details of a specific order."""
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product__images'),
        id=order_id
    )
    if order.user != request.user and not request.user.is_staff:
        messages.error(request, "You do not have permission to view this order.")
        return redirect('app1:order_history')

    order_items = order.items.all()
    return render(request, 'order_detail.html', {'order': order, 'order_items': order_items})

@csrf_exempt
def payment_success_view(request):
    messages.info(request, "Payment success endpoint reached (Currently bypassed).")
    return redirect('app1:order_history')


def payment_failed_view(request):
    messages.error(request, "Payment failed or was cancelled. Please try checkout again.")
    return redirect('app1:checkout')