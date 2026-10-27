from decimal import Decimal
from store.models import Product, Cart as DBCart, CartItem as DBCartItem

class Cart:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        
        if override_quantity:
            self.cart[product_id]['quantity'] = int(quantity)
        else:
            self.cart[product_id]['quantity'] += int(quantity)
        
        # Don't allow quantity to exceed current stock
        if self.cart[product_id]['quantity'] > product.stock:
            self.cart[product_id]['quantity'] = product.stock

        if self.cart[product_id]['quantity'] <= 0:
            self.remove(product)
        else:
            self.save()
            self._sync_db()

    def update(self, product, quantity):
        quantity = int(quantity)
        if quantity <= 0:
            self.remove(product)
        else:
            self.add(product=product, quantity=quantity, override_quantity=True)

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
            self._sync_db()

    def clear(self):
        if 'cart' in self.session:
            del self.session['cart']
        self.cart = {}
        self.save()
        self._sync_db(clear_all=True)

    def save(self):
        self.session['cart'] = self.cart
        self.session.modified = True

    def _sync_db(self, clear_all=False):
        """Optionally syncs session cart state to database for authenticated users."""
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            try:
                db_cart, _ = DBCart.objects.get_or_create(user=self.request.user)
                if clear_all:
                    db_cart.items.all().delete()
                else:
                    # Update DB items from session
                    existing_items = {str(item.product_id): item for item in db_cart.items.all()}
                    current_ids = set(self.cart.keys())

                    # Delete removed
                    for pid, item in existing_items.items():
                        if pid not in current_ids:
                            item.delete()

                    # Add or update
                    for pid, item_data in self.cart.items():
                        product = Product.objects.filter(id=int(pid), is_active=True).first()
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
                        # Combine quantity, bound by stock
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
        product_ids = [int(k) for k in self.cart.keys() if k.isdigit()]
        products = Product.objects.filter(id__in=product_ids)
        product_map = {product.id: product for product in products}

        cart = self.cart.copy()
        for pid_str, item in list(cart.items()):
            try:
                pid = int(pid_str)
                product = product_map.get(pid)
                if product and product.is_active:
                    item['product'] = product
                    # Recalculate using live database price
                    item['price'] = product.price
                    item['line_total'] = item['price'] * item['quantity']
                    yield item
                else:
                    # Stale or inactive product
                    del self.cart[pid_str]
                    self.save()
            except (ValueError, TypeError):
                continue

    def __len__(self):
        return sum(item.get('quantity', 0) for item in self.cart.values())

    def get_subtotal(self):
        subtotal = Decimal('0.00')
        for item in self:
            subtotal += item['line_total']
        return subtotal

    def get_shipping_cost(self):
        return Decimal('0.00')  # Free delivery Nationwide

    def get_total(self):
        return self.get_subtotal() + self.get_shipping_cost()
