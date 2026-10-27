from django.contrib import admin
from django.utils.html import format_html
from store.models import Category, Product, Order, OrderItem, UserProfile, Cart, CartItem


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'state', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone', 'city')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'original_price', 'stock', 'is_active', 'is_featured', 'created_at')
    list_filter = ('is_active', 'is_featured', 'category', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    list_editable = ('price', 'stock', 'is_active', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'unit_price', 'quantity', 'line_total')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'full_name', 'phone', 'total', 'status_badge', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'full_name', 'phone', 'user__username', 'user__email')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'subtotal', 'shipping_cost', 'total')
    inlines = [OrderItemInline]
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']

    def status_badge(self, obj):
        colors = {
            'Placed': '#2563EB',
            'Processing': '#D97706',
            'Shipped': '#7C3AED',
            'Delivered': '#059669',
            'Cancelled': '#DC2626',
        }
        color = colors.get(obj.status, '#4B5563')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 9999px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.status
        )
    status_badge.short_description = 'Status'

    @admin.action(description="Mark selected orders as Processing")
    def mark_as_processing(self, request, queryset):
        queryset.update(status='Processing')

    @admin.action(description="Mark selected orders as Shipped")
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='Shipped')

    @admin.action(description="Mark selected orders as Delivered & Paid")
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='Delivered', payment_status='Paid')

    @admin.action(description="Mark selected orders as Cancelled")
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='Cancelled')


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'created_at', 'updated_at')
    inlines = [CartItemInline]
