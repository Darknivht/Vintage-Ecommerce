from django import forms
from django.core.exceptions import ValidationError
from .models import Listing, Category, ListingInquiry

LISTING_TYPE_CHOICES = [
    ('for_sale', 'For Sale'),
    ('for_rent', 'For Rent'),
    ('service', 'Service'),
    ('job', 'Job'),
    ('wanted', 'Wanted'),
]

PRICE_TYPE_CHOICES = [
    ('fixed', 'Fixed Price'),
    ('negotiable', 'Negotiable'),
    ('auction', 'Auction'),
    ('free', 'Free'),
]

STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('published', 'Published'),
    ('sold', 'Sold'),
    ('rented', 'Rented'),
    ('expired', 'Expired'),
]

CONDITION_CHOICES = [
    ('new', 'New'),
    ('like_new', 'Like New'),
    ('good', 'Good'),
    ('fair', 'Fair'),
    ('poor', 'Poor'),
]

class ListingForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'categorySelect'
        })
    )
    
    subcategory = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'subcategorySelect'
        })
    )
    
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter listing title'
        })
    )
    
    short_description = forms.CharField(
        max_length=300,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Brief description (optional)'
        })
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Detailed description of your listing'
        })
    )
    
    price = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter price',
            'step': '0.01'
        })
    )
    
    price_type = forms.ChoiceField(
        choices=PRICE_TYPE_CHOICES,
        initial='fixed',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    listing_type = forms.ChoiceField(
        choices=LISTING_TYPE_CHOICES,
        initial='for_sale',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    condition = forms.ChoiceField(
        choices=CONDITION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    location = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City, State'
        })
    )
    
    address = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Detailed address (optional)'
        })
    )
    
    contact_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contact phone number'
        })
    )
    
    contact_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contact email'
        })
    )
    
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    video_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'YouTube or video URL (optional)'
        })
    )
    
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter tags separated by commas'
        })
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        initial='draft',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    featured = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    urgent = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    negotiable = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Listing
        fields = [
            'title', 'short_description', 'description', 'category', 'subcategory',
            'listing_type', 'price', 'price_type', 'condition', 'location', 'address',
            'contact_phone', 'contact_email', 'image', 'video_url', 'tags',
            'status', 'featured', 'urgent', 'negotiable'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If editing existing listing, load subcategories for the selected category
        if self.instance.pk and self.instance.category:
            self.fields['subcategory'].queryset = Category.objects.filter(
                parent=self.instance.category
            )

    def clean_price(self):
        price = self.cleaned_data.get('price')
        price_type = self.cleaned_data.get('price_type')
        
        if price_type != 'free' and not price:
            raise ValidationError("Price is required for non-free listings.")
        
        if price and price <= 0:
            raise ValidationError("Price must be greater than 0.")
        
        return price

    def clean_title(self):
        title = self.cleaned_data.get('title')
        
        if len(title.split()) < 3:
            raise ValidationError("Title should contain at least 3 words.")
        
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        
        if len(description.split()) < 10:
            raise ValidationError("Description should contain at least 10 words.")
        
        return description


class ListingFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search listings...'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(type="listing", parent=None),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'categorySelect'
        })
    )
    
    subcategory = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        empty_label="All Subcategories",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'subcategorySelect'
        })
    )
    
    listing_type = forms.ChoiceField(
        choices=[('', 'All Types')] + LISTING_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    price_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price'
        })
    )
    
    price_max = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price'
        })
    )
    
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Location'
        })
    )
    
    condition = forms.ChoiceField(
        choices=[('', 'Any Condition')] + CONDITION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
            ('price', 'Price: Low to High'),
            ('-price', 'Price: High to Low'),
            ('-views_count', 'Most Viewed'),
            ('title', 'Title A-Z'),
        ],
        initial='-created_at',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If category is selected, populate subcategories
        if self.data.get('category'):
            try:
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = Category.objects.filter(
                    parent_id=category_id, type="listing"
                )
            except (ValueError, TypeError):
                pass


class ListingInquiryForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your full name'
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email address'
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your phone number (optional)'
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Your message to the seller...'
        })
    )

    class Meta:
        model = ListingInquiry
        fields = ['name', 'email', 'phone', 'message']

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Pre-fill with user data if authenticated
        if user and user.is_authenticated:
            self.fields['name'].initial = user.get_full_name() or user.username
            self.fields['email'].initial = user.email


class VendorListingFilterForm(forms.Form):
    STATUS_CHOICES = [
        ('all', 'All'),
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('sold', 'Sold'),
        ('expired', 'Expired'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        initial='all',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search your listings...'
        })
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
            ('title', 'Title A-Z'),
            ('-views_count', 'Most Viewed'),
            ('-price', 'Highest Price'),
            ('price', 'Lowest Price'),
        ],
        initial='-created_at',
        widget=forms.Select(attrs={'class': 'form-select'})
    )