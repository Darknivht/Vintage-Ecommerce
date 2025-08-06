from django import forms
from store.models import Listing, CategorySchema, Category
import json

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'category', 'description', 'price', 'location', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit to listing categories only
        self.fields['category'].queryset = Category.objects.filter(type="listing")

        # Add consistent styling to standard fields
        self.fields['title'].widget.attrs.update({'class': 'form-control rounded'})
        self.fields['description'].widget.attrs.update({'class': 'form-control rounded'})
        self.fields['price'].widget.attrs.update({'class': 'form-control rounded'})
        self.fields['location'].widget.attrs.update({'class': 'form-control rounded'})
        self.fields['image'].widget.attrs.update({'class': 'form-control rounded'})

        # If editing, get category from instance or POST
        category = None
        if self.instance and self.instance.pk:
            category = self.instance.category
        elif 'category' in self.data:
            try:
                category = Listing._meta.get_field('category').related_model.objects.get(pk=self.data['category'])
            except Exception:
                pass

        # Add dynamic fields based on schema
        if category:
            try:
                schema = CategorySchema.objects.get(category=category)
                fields_def = schema.schema.get('fields', [])
                for field in fields_def:
                    field_name = field['name']
                    field_label = field.get('label', field_name.capitalize())
                    field_type = field.get('type', 'text')

                    if field_type == 'text':
                        self.fields[field_name] = forms.CharField(label=field_label, required=False, widget=forms.TextInput(attrs={'class': 'form-control rounded'}))
                    elif field_type == 'number':
                        self.fields[field_name] = forms.DecimalField(label=field_label, required=False, widget=forms.NumberInput(attrs={'class': 'form-control rounded'}))
                    elif field_type == 'boolean':
                        self.fields[field_name] = forms.BooleanField(label=field_label, required=False)
                    elif field_type == 'date':
                        self.fields[field_name] = forms.DateField(label=field_label, required=False, widget=forms.DateInput(attrs={'class': 'form-control rounded', 'type': 'date'}))

                    if self.instance and self.instance.extra_data:
                        self.fields[field_name].initial = self.instance.extra_data.get(field_name)
            except CategorySchema.DoesNotExist:
                pass

    def clean(self):
        cleaned_data = super().clean()
        extra_data = {}

        for field in self.fields:
            if field not in self.Meta.fields:
                extra_data[field] = cleaned_data.get(field)

        self.instance.extra_data = extra_data
        return cleaned_data
