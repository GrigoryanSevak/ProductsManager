from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect
from django.utils.html import mark_safe
from django.shortcuts import render
from .forms import TempImagesUploadForm
from .models import TempImage, TempProduct
from django.contrib.admin import SimpleListFilter

class TempImagesAdmin(admin.ModelAdmin):
    list_display = ('product', 'sort_order', 'title', 'width', 'height', 'file_size', 'remove_bg', 'remove_wm')
    search_fields = ('product', 'title',)
    list_filter = ('product__product_id', 'width', 'height', 'remove_bg', 'remove_wm', 'created_at')
    list_editable = ('remove_bg', 'remove_wm', 'sort_order')  # Include sort_order here

class TempImagesInline(admin.TabularInline):
    model = TempImage
    fields = ('image_preview', 'file', 'sort_order', 'remove_bg', 'remove_wm', 'caption', 'title')
    readonly_fields = ('image_preview', 'file', 'caption')  # Remove sort_order, remove_bg, remove_wm from here
    extra = 0
    search_fields = ['caption', 'file']

    def image_preview(self, obj):
        if obj.file:
            return mark_safe(f'<img src="{obj.file.url}" style="width: 100px; height: auto;" />')
        return None
    image_preview.short_description = 'Preview'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')

class TempProductsAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'title', 'view_images_link',)
    search_fields = ('product_id', 'title',)
    inlines = [TempImagesInline]
    actions = ['mark_images_for_bg_removal', 'mark_images_for_wm_removal']

    def view_images_link(self, obj):
        url = reverse('admin:products_tempproductstable_view_images', args=[obj.product_id])
        return mark_safe(f'<a href="{url}">Посмотреть изображения</a>')

    view_images_link.short_description = 'View Images'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:product_id>/images/', self.admin_site.admin_view(self.view_images), name='products_tempproductstable_view_images'),
        ]
        return custom_urls + urls

    def view_images(self, request, product_id):
        product = TempProduct.objects.get(product_id=product_id)
        products_list = TempProduct.objects.all().order_by("id")
        images = TempImage.objects.filter(product=product).order_by('sort_order')
        sort_order = max(item.sort_order for item in images) + 1 if images else 1

        if request.method == 'POST':
            for image in images:
                delete_image_field = f'delete_image_{image.id}'
                if delete_image_field in request.POST:
                    image.delete()
                    return redirect('admin:products_tempproductstable_view_images', product_id=product.product_id)

                remove_bg_field = f'remove_bg_{image.id}'
                remove_wm_field = f'remove_wm_{image.id}'
                sort_order_field = f'sort_order_{image.id}'

                if remove_bg_field in request.POST:
                    image.remove_bg = request.POST[remove_bg_field] == 'on'
                else:
                    image.remove_bg = False

                if remove_wm_field in request.POST:
                    image.remove_wm = request.POST[remove_wm_field] == 'on'
                else:
                    image.remove_wm = False

                if sort_order_field in request.POST:
                    image.sort_order = int(request.POST[sort_order_field])

                image.save()

            if 'file' in request.FILES:
                form = TempImagesUploadForm(request.POST, request.FILES)
                if form.is_valid():
                    new_image = form.save(commit=False)
                    new_image.product = product
                    new_image.save()
                    return redirect('admin:products_tempproductstable_view_images', product_id=product.product_id)
                else:
                    print('Form is not valid:', form.errors)

            return redirect('admin:products_tempproductstable_view_images', product_id=product.product_id)

        form = TempImagesUploadForm(initial={'product': product.product_id, 'sort_order': sort_order})

        context = {
            'product': product,
            'images': images,
            'title': product.title,
            'form': form,
            'sort_order': sort_order,
            'products_list': products_list,
        }
        return render(request, 'products/view_images.html', context)

    def has_add_permission(self, request, obj=None):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff

    def mark_images_for_bg_removal(self, request, queryset):
        count = queryset.update(remove_bg=True)
        self.message_user(request, f'{count} images marked for background removal.')
    mark_images_for_bg_removal.short_description = "Mark images for background removal"

    def mark_images_for_wm_removal(self, request, queryset):
        count = queryset.update(remove_wm=True)
        self.message_user(request, f'{count} images marked for watermark removal.')
    mark_images_for_wm_removal.short_description = "Mark images for watermark removal"

admin.site.register(TempProduct, TempProductsAdmin)
admin.site.register(TempImage, TempImagesAdmin)