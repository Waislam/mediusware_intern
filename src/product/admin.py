from django.contrib import admin

from .models import Variant, Product, ProductVariant, ProductVariantPrice
# Register your models here.
admin.site.register(Variant)
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(ProductVariantPrice)
