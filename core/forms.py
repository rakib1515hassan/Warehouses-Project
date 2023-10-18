from django import forms
from .models import Warehouse, WarehousePhoto


class WarehouseForm(forms.ModelForm):
    location_coordinates = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'location-coordinates'}), required=False)
    photos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    class Meta:
        model = Warehouse
        fields = "__all__"
        exclude = ["owner", "location", "coordinates"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.ChoiceField):
                field.widget.attrs.update({'class': 'form-select'})
            elif not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})



