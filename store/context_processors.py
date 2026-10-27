from store.cart import Cart
from store.models import Category

def cart_context(request):
    cart = Cart(request)
    categories = Category.objects.filter(is_active=True).order_by('name')
    return {
        'cart': cart,
        'cart_count': len(cart),
        'nav_categories': categories,
    }
