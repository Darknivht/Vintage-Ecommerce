from django import forms
from store.models import Listing, CategorySchema
import json

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'category', 'description', 'price', 'cover_image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If editing, we need the category from the instance
        category = None
        if self.instance and self.instance.pk:
            category = self.instance.category
        else:
            # If new, try to extract from POST data
            if 'category' in self.data:
                try:
                    category = Listing._meta.get_field('category').related_model.objects.get(pk=self.data['category'])
                except Exception:
                    pass

        # Dynamically add fields based on category schema
        if category:
            try:
                schema = CategorySchema.objects.get(category=category)
                fields_def = schema.schema.get('fields', [])
                for field in fields_def:
                    field_name = field['name']
                    field_label = field.get('label', field_name.capitalize())
                    field_type = field.get('type', 'text')

                    if field_type == 'text':
                        self.fields[field_name] = forms.CharField(label=field_label, required=False)
                    elif field_type == 'number':
                        self.fields[field_name] = forms.DecimalField(label=field_label, required=False)
                    elif field_type == 'boolean':
                        self.fields[field_name] = forms.BooleanField(label=field_label, required=False)
                    elif field_type == 'date':
                        self.fields[field_name] = forms.DateField(label=field_label, required=False)
                    # Add more field types as needed (e.g., select, multiselect)
                    # elif field_type == 'select':
                    #     self.fields[field_name] = forms.ChoiceField(...)

                    # If editing, prefill field from extra_data
                    if self.instance and self.instance.extra_data:
                        self.fields[field_name].initial = self.instance.extra_data.get(field_name, None)

            except CategorySchema.DoesNotExist:
                pass

    def clean(self):
        cleaned_data = super().clean()
        extra_data = {}

        # Save dynamic fields into extra_data
        for field in self.fields:
            if field not in self.Meta.fields:
                extra_data[field] = cleaned_data.get(field)

        self.instance.extra_data = extra_data
        return cleaned_data
