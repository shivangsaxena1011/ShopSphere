import uuid
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from store.models import Order, OrderItem, Product

def create_order_from_cart(user, cart, checkout_data):
    """
    Atomically creates an Order from the Cart, decrements stock, and stores item snapshots.
    Guarantees rollback if stock is insufficient or concurrent updates occur.
    """
    if len(cart) == 0:
        raise ValidationError("Cannot checkout with an empty shopping cart.")

    with transaction.atomic():
        order_items_to_create = []
        subtotal = Decimal('0.00')

        # 1. Lock and validate stock for all products in cart
        for item in cart:
            product = Product.objects.select_for_update().get(id=item['product'].id)
            requested_qty = item['quantity']

            if not product.is_active:
                raise ValidationError(f"Product '{product.name}' is no longer active.")
            if product.stock < requested_qty:
                raise ValidationError(
                    f"Insufficient stock for '{product.name}'. Available: {product.stock}, requested: {requested_qty}."
                )

            line_total = product.price * requested_qty
            subtotal += line_total
            order_items_to_create.append({
                'product': product,
                'name': product.name,
                'unit_price': product.price,
                'quantity': requested_qty,
                'line_total': line_total,
            })

        # 2. Generate unique order number and calculate totals
        order_number = f"SS{uuid.uuid4().hex[:8].upper()}"
        shipping = cart.get_shipping_cost()
        total = subtotal + shipping

        # 3. Create the order
        order = Order.objects.create(
            user=user,
            order_number=order_number,
            full_name=checkout_data.get('full_name', '').strip(),
            phone=checkout_data.get('phone', '').strip(),
            address=checkout_data.get('address', '').strip(),
            city=checkout_data.get('city', '').strip(),
            state=checkout_data.get('state', '').strip(),
            postal_code=checkout_data.get('postal_code', '').strip(),
            subtotal=subtotal,
            shipping_cost=shipping,
            total=total,
            payment_method='Cash on Delivery (COD)',
            payment_status='Pending',
            status='Placed',
            notes=checkout_data.get('notes', '').strip()
        )

        # 4. Create historical snapshots & decrement inventory
        for item_data in order_items_to_create:
            product = item_data['product']
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=item_data['name'],
                unit_price=item_data['unit_price'],
                quantity=item_data['quantity'],
                line_total=item_data['line_total']
            )
            product.stock -= item_data['quantity']
            product.save(update_fields=['stock'])

        # 5. Clear cart only upon successful transaction commit
        cart.clear()

        return order
