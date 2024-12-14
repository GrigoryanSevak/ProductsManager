from django import forms
from .models import TempImage

class TempImagesUploadForm(forms.ModelForm):
    class Meta:
        model = TempImage
        fields = ['product', 'caption', 'file', 'sort_order', 'collection_id', 'remove_wm', 'remove_bg']
        widgets = {
            'product': forms.HiddenInput(),
            'caption': forms.TextInput(attrs={'placeholder': 'Enter caption', 'class': 'form-control caption-input'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control file-input'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control sort-order-input'}),
            'collection_id': forms.TextInput(attrs={'class': 'form-control collection-input', 'readonly': True}),
            'remove_wm': forms.CheckboxInput(attrs={'class': 'form-check-input remove-wm-checkbox'}),
            'remove_bg': forms.CheckboxInput(attrs={'class': 'form-check-input remove-bg-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        sort_order = kwargs.get('initial', {}).get('sort_order', None)
        product = kwargs.get('initial', {}).get('product', None)
        super().__init__(*args, **kwargs)

        if sort_order:
            self.fields['sort_order'].widget.attrs['placeholder'] = sort_order
            self.fields['caption'].widget.attrs['value'] = f"{product}_{sort_order}_image"
            self.fields['collection_id'].widget.attrs['value'] = "1"