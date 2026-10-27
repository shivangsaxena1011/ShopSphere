from decimal import Decimal
from store.models import Product, Cart as DBCart, CartItem as DBCartItem

COUPON_DISCOUNTS = {
    'SHOPSPHERE10': {'type': 'percent', 'value': Decimal('0.10'), 'label': '10% Discount'},
    'FIRSTBUY': {'type': 'flat', 'value': Decimal('200.00'), 'label': '₹200 Welcome Offer'},
}

class Cart:
    def __init__(self, request):
        self.request = request
        self.session = getattr(request, 'session', {})
        cart = self.session.get('cart')
        if cart is None:
            if hasattr(self.session, '__setitem__'):
                cart = self.session['cart'] = {}
            else:
                cart = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}

        qty = int(quantity)
        if override_quantity:
            self.cart[product_id]['quantity'] = qty
        else:
            self.cart[product_id]['quantity'] += qty

        # Don't allow quantity to exceed current stock
        if self.cart[product_id]['quantity'] > product.stock:
            self.cart[product_id]['quantity'] = product.stock

        if self.cart[product_id]['quantity'] <= 0:
            self.remove(product)
        else:
            self.save()
            self._sync_db()

    def update(self, product, quantity):
        qty = int(quantity)
        if qty <= 0:
            self.remove(product)
        else:
            self.add(product=product, quantity=qty, override_quantity=True)

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
            self._sync_db()

    def clear(self):
        if 'cart' in self.session:
            del self.session['cart']
        if 'coupon_code' in self.session:
            del self.session['coupon_code']
        self.cart = {}
        self.save()
        self._sync_db(clear_all=True)

    def save(self):
        if hasattr(self.session, '__setitem__'):
            self.session['cart'] = self.cart
            self.session.modified = True

    def apply_coupon(self, code):
        code = str(code).strip().upper()
        if code in COUPON_DISCOUNTS:
            self.session['coupon_code'] = code
            self.session.modified = True
            return True, f"Coupon '{code}' applied successfully!"
        return False, "Invalid promotional coupon code."

    def remove_coupon(self):
        if 'coupon_code' in self.session:
            del self.session['coupon_code']
            self.session.modified = True

    @property
    def coupon_code(self):
        return self.get_coupon_code() or None

    def get_coupon_code(self):
        return self.session.get('coupon_code', '')

    def get_discount(self):
        code = self.get_coupon_code()
        if code in COUPON_DISCOUNTS:
            subtotal = self.get_subtotal()
            config = COUPON_DISCOUNTS[code]
            if config['type'] == 'percent':
                return (subtotal * config['value']).quantize(Decimal('0.01'))
            elif config['type'] == 'flat':
                return min(config['value'], subtotal)
        return Decimal('0.00')

    def get_discount_amount(self):
        return self.get_discount()

    def get_total_price(self):
        return self.get_total()

    def _sync_db(self, clear_all=False):
        """Optionally syncs session cart state to database for authenticated users."""
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            try:
                db_cart, _ = DBCart.objects.get_or_create(user=self.request.user)
                if clear_all:
                    db_cart.items.all().delete()
                else:
                    existing_items = {str(item.product_id): item for item in db_cart.items.all()}
                    current_ids = set(str(k) for k in self.cart.keys())

                    # Delete removed
                    for pid, item in existing_items.items():
                        if pid not in current_ids:
                            item.delete()

                    # Add or update
                    for pid, item_data in self.cart.items():
                        try:
                            prod_id = int(pid)
                        except (ValueError, TypeError):
                            continue
                        product = Product.objects.filter(id=prod_id, is_active=True).first()
                        if product:
                            DBCartItem.objects.update_or_create(
                                cart=db_cart,
                                product=product,
                                defaults={'quantity': item_data['quantity']}
                            )
            except Exception:
                pass

    def merge_from_db_to_session(self, user):
        """When user logs in, load any DB cart items and merge with existing session cart."""
        try:
            db_cart = DBCart.objects.filter(user=user).first()
            if db_cart:
                for db_item in db_cart.items.select_related('product').all():
                    pid = str(db_item.product.id)
                    if pid in self.cart:
                        combined = self.cart[pid]['quantity'] + db_item.quantity
                        self.cart[pid]['quantity'] = min(combined, db_item.product.stock)
                    else:
                        self.cart[pid] = {
                            'quantity': min(db_item.quantity, db_item.product.stock),
                            'price': str(db_item.product.price)
                        }
                self.save()
                self._sync_db()
        except Exception:
            pass

    def __iter__(self):
        product_ids = [int(k) for k in self.cart.keys() if str(k).isdigit()]
        products = Product.objects.filter(id__in=product_ids)
        product_map = {product.id: product for product in products}

        cart = self.cart.copy()
        for pid_str, item in list(cart.items()):
            try:
                pid = int(pid_str)
                product = product_map.get(pid)
                if product and product.is_active:
                    item['product'] = product
                    item['price'] = product.price
                    item['line_total'] = item['price'] * item['quantity']
                    yield item
                else:
                    # Remove stale / deleted item
                    if pid_str in self.cart:
                        del self.cart[pid_str]
                    self.save()
            except (ValueError, TypeError):
                continue

    def __len__(self):
        return sum(item.get('quantity', 0) for item in self.cart.values() if isinstance(item, dict))

    def get_subtotal(self):
        subtotal = Decimal('0.00')
        for item in self:
            subtotal += item['line_total']
        return subtotal

    def get_shipping_cost(self):
        return Decimal('0.00')  # Free delivery Nationwide

    def get_total(self):
        total = self.get_subtotal() - self.get_discount() + self.get_shipping_cost()
        return max(total, Decimal('0.00'))
