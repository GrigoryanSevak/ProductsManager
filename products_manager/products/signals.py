from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import TempImage
from .utils import get_image_size, hash_file


@receiver(pre_save, sender=TempImage)
def set_image_properties_pre_save(sender, instance, **kwargs):
    if instance.file:
        instance.title = f"{instance.product.product_id}-{instance.sort_order}"


@receiver(post_save, sender=TempImage)
def set_image_properties_post_save(sender, instance, created, **kwargs):
    if instance.file and created:
        file_path = instance.file.path
        image_data = get_image_size(file_path)
        
        instance.width = image_data['width']
        instance.height = image_data['height']
        instance.file_size = image_data['size']

        instance.file_hash = hash_file(file_path, 'sha256')
        
        instance.save()
