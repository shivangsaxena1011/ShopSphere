from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from store.models import Category, Product, Order, OrderItem
from store.cart import Cart
from store.services import create_order_from_cart


class ShopSphereModelAndCartTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Audio & Headphones",
            slug="audio-and-headphones",
            icon_name="headphones"
        )
        self.product = Product.objects.create(
            category=self.category,
            name="Wireless Headphones Pro",
            slug="wireless-headphones-pro",
            description="High fidelity noise cancelling audio.",
            price=Decimal("2999.00"),
            stock=10,
            is_active=True,
            is_featured=True
        )
        self.user = User.objects.create_user(
            username="testbuyer",
            email="testbuyer@shopsphere.local",
            password="password123"
        )
        self.client = Client()

    def test_category_slug_auto_generation(self):
        cat = Category.objects.create(name="Modern Wearables")
        self.assertEqual(cat.slug, "modern-wearables")

    def test_product_in_stock_and_price_defaults(self):
        self.assertTrue(self.product.in_stock)
        self.assertGreater(self.product.original_price, self.product.price)

    def test_session_cart_workflow(self):
        # 1. Add to cart
        response = self.client.post(
            reverse('cart_add', kwargs={'product_id': self.product.id}),
            {'quantity': 2}
        )
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertIn('cart', session)
        self.assertEqual(session['cart'][str(self.product.id)]['quantity'], 2)

        # 2. Update cart
        response = self.client.post(
            reverse('cart_update'),
            {'product_id': self.product.id, 'quantity': 5}
        )
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertEqual(session['cart'][str(self.product.id)]['quantity'], 5)

        # 3. Remove from cart
        response = self.client.post(
            reverse('cart_remove', kwargs={'product_id': self.product.id})
        )
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertNotIn(str(self.product.id), session['cart'])


class ShopSphereCheckoutAndSecurityTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Gadgets", slug="gadgets")
        self.product = Product.objects.create(
            category=self.category,
            name="Smart Fitness Tracker",
            slug="smart-fitness-tracker",
            description="Activity tracker with heart rate sensor.",
            price=Decimal("1999.00"),
            stock=3,
            is_active=True
        )
        self.user_a = User.objects.create_user(
            username="usera", email="usera@example.com", password="passwordA123"
        )
        self.user_b = User.objects.create_user(
            username="userb", email="userb@example.com", password="passwordB123"
        )
        self.client = Client()

    def test_atomic_checkout_success_and_stock_decrement(self):
        self.client.login(username="usera", password="passwordA123")
        # Add 2 items to cart
        self.client.post(reverse('cart_add', kwargs={'product_id': self.product.id}), {'quantity': 2})

        checkout_data = {
            'full_name': 'User A',
            'phone': '+91 9988776655',
            'address': 'Flat 101, Galaxy Apts',
            'city': 'Bhopal',
            'state': 'Madhya Pradesh',
            'postal_code': '462001',
            'notes': 'Call before delivery'
        }

        response = self.client.post(reverse('checkout'), checkout_data)
        self.assertEqual(response.status_code, 302)

        # Verify Order created
        order = Order.objects.filter(user=self.user_a).first()
        self.assertIsNotNone(order)
        self.assertTrue(order.order_number.startswith("SS"))
        self.assertEqual(order.total, Decimal("3998.00"))
        self.assertEqual(order.payment_method, "Cash on Delivery (COD)")

        # Verify atomic stock decrement
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 1)  # 3 - 2 = 1

    def test_insufficient_stock_rollback(self):
        self.client.login(username="usera", password="passwordA123")
        cart = Cart(self.client)
        cart.cart[str(self.product.id)] = {'quantity': 10, 'price': str(self.product.price)}
        cart.save()

        checkout_data = {
            'full_name': 'User A',
            'phone': '1234567890',
            'address': 'Street 1',
            'city': 'Bhopal',
            'state': 'MP',
            'postal_code': '462001'
        }

        with self.assertRaises(ValidationError):
            create_order_from_cart(self.user_a, cart, checkout_data)

        # Confirm stock was NOT changed
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

    def test_idor_order_ownership_protection(self):
        # Create order owned by User A
        order = Order.objects.create(
            user=self.user_a,
            order_number="SS11223344",
            full_name="User A",
            phone="1234567890",
            address="Street 1",
            city="Bhopal",
            state="MP",
            postal_code="462001",
            subtotal=Decimal("1999.00"),
            shipping_cost=Decimal("0.00"),
            total=Decimal("1999.00"),
            payment_method="Cash on Delivery (COD)",
            payment_status="Pending",
            status="Placed"
        )

        # User B logs in and attempts to access User A's order
        self.client.login(username="userb", password="passwordB123")
        response = self.client.get(reverse('order_detail', kwargs={'order_number': order.order_number}))
        # Must return 404 Not Found to prevent IDOR disclosure
        self.assertEqual(response.status_code, 404)


class ShopSphereSearchAndCatalogTests(TestCase):
    def setUp(self):
        self.cat1 = Category.objects.create(name="Books", slug="books")
        self.cat2 = Category.objects.create(name="Electronics", slug="electronics")
        Product.objects.create(
            category=self.cat1,
            name="Django for Beginners",
            slug="django-for-beginners",
            description="Build websites with Python and Django.",
            price=Decimal("499.00"),
            stock=20,
            is_active=True
        )
        Product.objects.create(
            category=self.cat2,
            name="Mechanical Keyboard",
            slug="mechanical-keyboard",
            description="RGB mechanical keyboard with blue switches.",
            price=Decimal("2499.00"),
            stock=15,
            is_active=True
        )
        self.client = Client()

    def test_search_query_filter(self):
        response = self.client.get(reverse('product_list'), {'q': 'Django'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django for Beginners")
        self.assertNotContains(response, "Mechanical Keyboard")

    def test_category_filter(self):
        response = self.client.get(reverse('product_list'), {'category': 'electronics'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mechanical Keyboard")
        self.assertNotContains(response, "Django for Beginners")


class ShopSphereBugFixAndEnhancementTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Accessories", slug="accessories")
        self.product = Product.objects.create(
            category=self.cat,
            name="Ultra Fast Charger",
            slug="ultra-fast-charger",
            description="65W GaN Charger.",
            price=Decimal("1500.00"),
            stock=10,
            is_active=True
        )
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="Password123!"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="Password123!"
        )
        self.client = Client()

    def test_slug_collision_resolution(self):
        # Create second product with identical name -> slug should append -1, -2, etc.
        p2 = Product.objects.create(
            category=self.cat,
            name="Ultra Fast Charger",
            description="Duplicate name charger",
            price=Decimal("1500.00"),
            stock=5,
            is_active=True
        )
        self.assertEqual(p2.slug, "ultra-fast-charger-1")

        # Create category with conflicting slug
        c2 = Category.objects.create(name="Accessories Extra", slug="accessories")
        self.assertEqual(c2.slug, "accessories-1")

    def test_coupon_discount_calculation_and_removal(self):
        self.client.login(username="user1", password="Password123!")
        # Add item to cart
        self.client.post(reverse('cart_add', kwargs={'product_id': self.product.id}), {'quantity': 1})

        # Apply SHOPSPHERE10 (10% discount)
        response = self.client.post(reverse('cart_apply_coupon'), {'coupon_code': 'SHOPSPHERE10'}, follow=True)
        self.assertEqual(response.status_code, 200)
        cart = Cart(self.client)
        self.assertEqual(cart.coupon_code, "SHOPSPHERE10")
        self.assertEqual(cart.get_discount_amount(), Decimal("150.00"))
        self.assertEqual(cart.get_total_price(), Decimal("1350.00"))

        # Remove coupon
        response = self.client.post(reverse('cart_remove_coupon'), follow=True)
        self.assertEqual(response.status_code, 200)
        cart = Cart(self.client)
        self.assertIsNone(cart.coupon_code)
        self.assertEqual(cart.get_discount_amount(), Decimal("0.00"))
        self.assertEqual(cart.get_total_price(), Decimal("1500.00"))

    def test_checkout_with_coupon_applies_to_order(self):
        self.client.login(username="user1", password="Password123!")
        self.client.post(reverse('cart_add', kwargs={'product_id': self.product.id}), {'quantity': 2}) # 3000.00
        self.client.post(reverse('cart_apply_coupon'), {'coupon_code': 'FIRSTBUY'}) # Flat 200 off

        checkout_data = {
            'full_name': 'Test User 1',
            'phone': '9876543210',
            'address': 'MG Road',
            'city': 'Indore',
            'state': 'MP',
            'postal_code': '452001'
        }
        response = self.client.post(reverse('checkout'), checkout_data)
        self.assertEqual(response.status_code, 302)

        order = Order.objects.filter(user=self.user1).latest('id')
        self.assertEqual(order.coupon_code, 'FIRSTBUY')
        self.assertEqual(order.discount_amount, Decimal('200.00'))
        self.assertEqual(order.subtotal, Decimal('3000.00'))
        self.assertEqual(order.total, Decimal('2800.00'))

    def test_profile_form_email_collision_prevented(self):
        from store.forms import UserProfileForm
        # Attempt to set user1's email to user2's email
        form = UserProfileForm(data={
            'first_name': 'User',
            'last_name': 'One',
            'email': 'user2@example.com', # Already taken by user2
            'phone': '1234567890',
            'address': 'Street',
            'city': 'Indore',
            'state': 'MP',
            'postal_code': '452001'
        }, instance=self.user1.profile, user=self.user1)

        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn("already in use", form.errors['email'][0])

    def test_login_redirect_preserves_next_param(self):
        # Put item in cart so /checkout/ doesn't redirect to /cart/
        self.client.post(reverse('cart_add', kwargs={'product_id': self.product.id}), {'quantity': 1})

        # Try accessing checkout while unauthenticated
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('next=/checkout/', response.url)

        # Login with next param
        login_response = self.client.post(
            reverse('login') + '?next=/checkout/',
            {'username': 'user1', 'password': 'Password123!'}
        )
        self.assertRedirects(login_response, '/checkout/')

