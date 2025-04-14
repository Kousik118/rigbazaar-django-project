from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Account, Product, ProductImage, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity', 'price')
    extra = 0
    can_delete = False
    verbose_name_plural = 'Items in this Order'

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    inlines = [ProductImageInline]
    list_per_page = 25

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_link', 'order_date', 'total_amount', 'order_status', 'razorpay_order_id') # Use user_link
    list_filter = ('order_status', 'order_date')
    search_fields = ('id', 'user__username', 'user__email', 'shipping_address', 'razorpay_order_id', 'razorpay_payment_id') # Added user email
    readonly_fields = ('user', 'order_date', 'total_amount', 'shipping_address',
                       'billing_address', 'razorpay_order_id', 'razorpay_payment_id',
                       'razorpay_signature')
    inlines = [OrderItemInline]
    list_per_page = 25
    date_hierarchy = 'order_date'

    def user_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        link = reverse("admin:app1_account_change", args=[obj.user.id]) # Assuming 'app1_account' is the name
        return format_html('<a href="{}">{}</a>', link, obj.user.username)
    user_link.short_description = 'User'

@admin.register(Account)
class AccountAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'phone', 'first_name', 'last_name', 'is_staff', 'profile_pic_thumbnail') # Added phone and pic
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Info', {'fields': ('phone', 'profile_pic')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Info', {'fields': ('phone', 'profile_pic')}),
    )
    search_fields = BaseUserAdmin.search_fields + ('phone', 'email')

    def profile_pic_thumbnail(self, obj):
        from django.utils.html import format_html
        if obj.profile_pic:
            return format_html('<img src="{}" style="width: 45px; height: 45px; border-radius: 50%;" />', obj.profile_pic.url)
        return "No Image"
    profile_pic_thumbnail.short_description = 'Profile Pic'
