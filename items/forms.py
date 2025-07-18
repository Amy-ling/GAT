from django import forms
from items.models import  Item



from django import forms
from items.models import  Item



from django import forms
from items.models import  Item



class MultipleFileInput(forms.ClearableFileInput):
    """
    A custom widget that allows for the selection of multiple files.
    """
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """
    A custom form field that uses the MultipleFileInput widget.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result




class ItemForm(forms.ModelForm):
    item_image = MultipleFileField(
        required=False,
        label="Upload Image(s) (Max 6)"
    )

    class Meta:
        model = Item
        fields = ['item_name', 'item_type', 'description', 'item_image']
        labels = {
            'item_name': 'Item Name',
            'item_type': 'Item Type',
            'description': 'Description',
        }

    def clean_item_image(self):
        images = self.files.getlist('item_image')
        if len(images) > 6:
            raise forms.ValidationError("You can only upload up to 6 images.")
        return images