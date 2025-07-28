from django import forms
from store.models import (
    Category, Product, RealEstateListing, VehicleListing, 
    JobListing, ServiceListing, Paybill
)

class CategorySelectForm(forms.Form):
    """Form for selecting a category to add a product to"""
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Select a category",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'category-select'})
    )


class ProductForm(forms.ModelForm):
    """Form for adding a regular product"""
    class Meta:
        model = Product
        fields = ['name', 'description', 'image', 'category', 'price', 'regular_price', 'stock', 'shipping', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'regular_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'shipping': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class RealEstateListingForm(forms.ModelForm):
    """Form for adding a real estate listing"""
    class Meta:
        model = RealEstateListing
        fields = ['title', 'description', 'category', 'state', 'local_government', 'neighborhood', 
                 'price', 'land_size', 'house_size', 'number_of_bedrooms', 'number_of_bathrooms', 
                 'images', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'local_government': forms.TextInput(attrs={'class': 'form-control'}),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'land_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'house_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'number_of_bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'number_of_bathrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class VehicleListingForm(forms.ModelForm):
    """Form for adding a vehicle listing"""
    class Meta:
        model = VehicleListing
        fields = ['title', 'description', 'category', 'brand', 'vehicle_type', 
                 'price', 'year', 'mileage', 'images', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class JobListingForm(forms.ModelForm):
    """Form for adding a job listing"""
    class Meta:
        model = JobListing
        fields = ['title', 'description', 'category', 'company', 'location', 
                 'salary_range', 'application_link', 'job_type', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'salary_range': forms.TextInput(attrs={'class': 'form-control'}),
            'application_link': forms.URLInput(attrs={'class': 'form-control'}),
            'job_type': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class ServiceListingForm(forms.ModelForm):
    """Form for adding a service listing"""
    class Meta:
        model = ServiceListing
        fields = ['title', 'description', 'category', 'service_type', 
                 'contact_phone', 'contact_email', 'service_area', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'service_type': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'service_area': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class PaybillForm(forms.ModelForm):
    """Form for adding a bill payment service"""
    class Meta:
        model = Paybill
        fields = ['title', 'description', 'category', 'service_category', 
                 'payment_provider', 'payment_code', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'service_category': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_provider': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_code': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }