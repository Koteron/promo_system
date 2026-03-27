from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from orders.models import (
    Good, 
    Order, 
    OrderItem, 
    Category,
    PromoCode,
    PromoCodeUsage,
)


User = get_user_model()
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(DefaultUserAdmin):
    list_display = ("id", "username", "email", "is_staff")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(Good)
class GoodAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'price', 'is_excluded_from_promotions', 'created_at']
    search_fields = ['name']
    list_filter = ['category', 'is_excluded_from_promotions', 'created_at']
    readonly_fields = ['created_at']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['price_per_unit', 'discount', 'total']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'final_price', 'promo_code', 'created_at']
    search_fields = ['user__username', 'promo_code__code']
    list_filter = ['status', 'created_at', 'promo_code']
    readonly_fields = ['total_price', 'final_price', 'created_at', 'updated_at']
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'good', 'quantity', 'price_per_unit', 'total']
    search_fields = ['order__id', 'good__name']
    list_filter = ['created_at']
    readonly_fields = ['discount', 'total']


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount', 'category', 'max_uses',
                     'current_uses', 'valid_until', 'is_expired']
    search_fields = ['code']
    list_filter = ['category', 'created_at', 'valid_until']
    readonly_fields = ['current_uses', 'created_at', 'updated_at', 'is_expired']
    fieldsets = (
        ('Code Information', {
            'fields': ('code', 'description')
        }),
        ('Discount Configuration', {
            'fields': ('discount', 'category')
        }),
        ('Usage Limits', {
            'fields': ('max_uses', 'current_uses')
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_until', 'is_expired')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PromoCodeUsage)
class PromoCodeUsageAdmin(admin.ModelAdmin):
    list_display = ['promo_code', 'user', 'order', 'used_at']
    search_fields = ['promo_code__code', 'user__username', 'order__id']
    list_filter = ['used_at', 'promo_code']
    readonly_fields = ['used_at']
