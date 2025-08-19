"""
Advanced Customer Engagement System for Vintage Ecommerce
Handles personalization, recommendations, and customer retention
"""

from django.db import models
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Avg, Sum, Q, F
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import random

from store.models import Product, Order, OrderItem, Review, Category, WishlistItem, RecentlyViewed
from userauths.models import User


class CustomerSegment(models.Model):
    """
    Customer segmentation for targeted marketing
    """
    SEGMENT_TYPES = [
        ('new_customer', 'New Customer'),
        ('regular_customer', 'Regular Customer'),
        ('vip_customer', 'VIP Customer'),
        ('at_risk', 'At Risk Customer'),
        ('dormant', 'Dormant Customer'),
        ('high_value', 'High Value Customer'),
        ('bargain_hunter', 'Bargain Hunter'),
        ('brand_loyal', 'Brand Loyal'),
    ]
    
    name = models.CharField(max_length=100)
    segment_type = models.CharField(max_length=20, choices=SEGMENT_TYPES)
    description = models.TextField()
    criteria = models.JSONField()  # Store segmentation criteria
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class CustomerProfile(models.Model):
    """
    Extended customer profile with engagement data
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    segment = models.ForeignKey(CustomerSegment, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Engagement metrics
    total_orders = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    average_order_value = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    last_order_date = models.DateTimeField(null=True, blank=True)
    
    # Preferences
    preferred_categories = models.ManyToManyField(Category, blank=True)
    preferred_price_range_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preferred_price_range_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Engagement tracking
    email_opens = models.PositiveIntegerField(default=0)
    email_clicks = models.PositiveIntegerField(default=0)
    website_visits = models.PositiveIntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    
    # Communication preferences
    email_marketing_consent = models.BooleanField(default=True)
    sms_marketing_consent = models.BooleanField(default=False)
    push_notifications_consent = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - Profile"
    
    def update_metrics(self):
        """Update customer metrics based on order history"""
        orders = Order.objects.filter(customer=self.user, payment_status='Paid')
        
        self.total_orders = orders.count()
        self.total_spent = orders.aggregate(total=Sum('total'))['total'] or 0
        self.average_order_value = orders.aggregate(avg=Avg('total'))['avg'] or 0
        self.last_order_date = orders.order_by('-date').first().date if orders.exists() else None
        
        # Update preferred categories based on purchase history
        category_counts = OrderItem.objects.filter(
            order__customer=self.user,
            order__payment_status='Paid'
        ).values('product__category').annotate(
            count=Count('id')
        ).order_by('-count')[:3]
        
        preferred_categories = [cc['product__category'] for cc in category_counts if cc['product__category']]
        self.preferred_categories.set(Category.objects.filter(id__in=preferred_categories))
        
        self.save()


class PersonalizationEngine:
    """
    AI-powered personalization engine
    """
    
    @staticmethod
    def get_product_recommendations(user, limit=10):
        """
        Get personalized product recommendations
        """
        if not user.is_authenticated:
            return Product.objects.filter(status='Published', featured=True)[:limit]
        
        recommendations = []
        
        # 1. Collaborative filtering - users who bought similar items
        user_orders = OrderItem.objects.filter(order__customer=user, order__payment_status='Paid')
        if user_orders.exists():
            # Get products bought by users with similar purchase history
            similar_products = Product.objects.filter(
                orderitem__order__customer__in=User.objects.filter(
                    customer_orders__orderitem__product__in=user_orders.values('product')
                ).exclude(id=user.id)
            ).exclude(
                id__in=user_orders.values('product')
            ).annotate(
                similarity_score=Count('orderitem')
            ).order_by('-similarity_score')[:limit//2]
            
            recommendations.extend(similar_products)
        
        # 2. Content-based filtering - similar categories
        profile = getattr(user, 'customer_profile', None)
        if profile and profile.preferred_categories.exists():
            category_products = Product.objects.filter(
                category__in=profile.preferred_categories.all(),
                status='Published'
            ).exclude(
                id__in=[p.id for p in recommendations]
            ).order_by('-view_count')[:limit//3]
            
            recommendations.extend(category_products)
        
        # 3. Recently viewed products (similar items)
        recently_viewed = RecentlyViewed.objects.filter(user=user)[:5]
        if recently_viewed.exists():
            viewed_categories = [rv.product.category for rv in recently_viewed if rv.product.category]
            similar_to_viewed = Product.objects.filter(
                category__in=viewed_categories,
                status='Published'
            ).exclude(
                id__in=[p.id for p in recommendations] + [rv.product.id for rv in recently_viewed]
            ).order_by('-view_count')[:limit//4]
            
            recommendations.extend(similar_to_viewed)
        
        # 4. Fill remaining slots with trending products
        remaining_slots = limit - len(recommendations)
        if remaining_slots > 0:
            trending = Product.objects.filter(
                status='Published'
            ).exclude(
                id__in=[p.id for p in recommendations]
            ).order_by('-view_count', '-date')[:remaining_slots]
            
            recommendations.extend(trending)
        
        return recommendations[:limit]
    
    @staticmethod
    def get_cross_sell_recommendations(product, limit=4):
        """
        Get cross-sell recommendations for a specific product
        """
        # Products frequently bought together
        frequently_bought_together = Product.objects.filter(
            orderitem__order__in=Order.objects.filter(
                orderitem__product=product,
                payment_status='Paid'
            )
        ).exclude(
            id=product.id
        ).annotate(
            frequency=Count('orderitem')
        ).order_by('-frequency')[:limit]
        
        return frequently_bought_together
    
    @staticmethod
    def get_upsell_recommendations(product, limit=3):
        """
        Get upsell recommendations (higher-priced similar products)
        """
        return Product.objects.filter(
            category=product.category,
            price__gt=product.price,
            status='Published'
        ).exclude(
            id=product.id
        ).order_by('price')[:limit]
    
    @staticmethod
    def segment_customer(user):
        """
        Automatically segment customer based on behavior
        """
        profile, created = CustomerProfile.objects.get_or_create(user=user)
        profile.update_metrics()
        
        # Segmentation logic
        days_since_last_order = None
        if profile.last_order_date:
            days_since_last_order = (timezone.now() - profile.last_order_date).days
        
        # New customer (less than 30 days, 0-1 orders)
        if user.date_joined > timezone.now() - timedelta(days=30) and profile.total_orders <= 1:
            segment_type = 'new_customer'
        
        # VIP customer (high value, frequent orders)
        elif profile.total_spent > 5000 and profile.total_orders > 10:
            segment_type = 'vip_customer'
        
        # High value customer
        elif profile.total_spent > 2000:
            segment_type = 'high_value'
        
        # At risk (no orders in 60+ days but was active)
        elif days_since_last_order and days_since_last_order > 60 and profile.total_orders > 2:
            segment_type = 'at_risk'
        
        # Dormant (no orders in 180+ days)
        elif days_since_last_order and days_since_last_order > 180:
            segment_type = 'dormant'
        
        # Regular customer
        elif profile.total_orders > 3:
            segment_type = 'regular_customer'
        
        else:
            segment_type = 'new_customer'
        
        # Get or create segment
        segment, created = CustomerSegment.objects.get_or_create(
            segment_type=segment_type,
            defaults={
                'name': segment_type.replace('_', ' ').title(),
                'description': f'Auto-generated {segment_type} segment'
            }
        )
        
        profile.segment = segment
        profile.save()
        
        return segment


class EmailCampaignManager:
    """
    Manage email marketing campaigns
    """
    
    @staticmethod
    def send_personalized_recommendations(user):
        """
        Send personalized product recommendations via email
        """
        if not user.email or not getattr(user, 'customer_profile', None):
            return False
        
        profile = user.customer_profile
        if not profile.email_marketing_consent:
            return False
        
        # Get recommendations
        recommendations = PersonalizationEngine.get_product_recommendations(user, limit=6)
        
        # Render email template
        context = {
            'user': user,
            'recommendations': recommendations,
            'unsubscribe_url': f"{settings.SITE_URL}/unsubscribe/{user.id}/"
        }
        
        html_content = render_to_string('emails/personalized_recommendations.html', context)
        text_content = render_to_string('emails/personalized_recommendations.txt', context)
        
        try:
            send_mail(
                subject=f"Hi {user.first_name}, we found some products you might love!",
                message=text_content,
                html_message=html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            # Track email sent
            profile.email_opens += 1
            profile.save()
            
            return True
        except Exception as e:
            print(f"Failed to send recommendation email: {e}")
            return False
    
    @staticmethod
    def send_abandoned_cart_reminder(user, cart_items):
        """
        Send abandoned cart reminder email
        """
        if not user.email:
            return False
        
        profile = getattr(user, 'customer_profile', None)
        if profile and not profile.email_marketing_consent:
            return False
        
        context = {
            'user': user,
            'cart_items': cart_items,
            'cart_total': sum(item.total for item in cart_items),
            'checkout_url': f"{settings.SITE_URL}/checkout/"
        }
        
        html_content = render_to_string('emails/abandoned_cart.html', context)
        text_content = render_to_string('emails/abandoned_cart.txt', context)
        
        try:
            send_mail(
                subject="Don't forget your items!",
                message=text_content,
                html_message=html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Failed to send abandoned cart email: {e}")
            return False
    
    @staticmethod
    def send_win_back_campaign(segment='at_risk'):
        """
        Send win-back campaign to at-risk customers
        """
        profiles = CustomerProfile.objects.filter(
            segment__segment_type=segment,
            email_marketing_consent=True
        )
        
        sent_count = 0
        for profile in profiles:
            user = profile.user
            
            # Create special discount code
            discount_code = f"COMEBACK{user.id}{random.randint(100, 999)}"
            
            context = {
                'user': user,
                'discount_code': discount_code,
                'discount_amount': 20,  # 20% discount
                'shop_url': f"{settings.SITE_URL}/shop/"
            }
            
            html_content = render_to_string('emails/win_back_campaign.html', context)
            text_content = render_to_string('emails/win_back_campaign.txt', context)
            
            try:
                send_mail(
                    subject=f"We miss you, {user.first_name}! Here's 20% off to welcome you back",
                    message=text_content,
                    html_message=html_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                sent_count += 1
            except Exception as e:
                print(f"Failed to send win-back email to {user.email}: {e}")
        
        return sent_count


# Views for customer engagement
@login_required
def personalized_dashboard(request):
    """
    Personalized customer dashboard
    """
    # Update customer segment
    PersonalizationEngine.segment_customer(request.user)
    
    # Get personalized recommendations
    recommendations = PersonalizationEngine.get_product_recommendations(request.user, limit=8)
    
    # Get recent orders
    recent_orders = Order.objects.filter(customer=request.user).order_by('-date')[:5]
    
    # Get wishlist items
    wishlist_items = WishlistItem.objects.filter(user=request.user)[:6]
    
    # Get recently viewed
    recently_viewed = RecentlyViewed.objects.filter(user=request.user)[:6]
    
    context = {
        'recommendations': recommendations,
        'recent_orders': recent_orders,
        'wishlist_items': wishlist_items,
        'recently_viewed': recently_viewed,
    }
    
    return render(request, 'customer/personalized_dashboard.html', context)


@login_required
def product_recommendations_api(request):
    """
    API endpoint for getting product recommendations
    """
    recommendation_type = request.GET.get('type', 'general')
    limit = int(request.GET.get('limit', 10))
    
    if recommendation_type == 'general':
        products = PersonalizationEngine.get_product_recommendations(request.user, limit)
    elif recommendation_type == 'cross_sell':
        product_id = request.GET.get('product_id')
        if product_id:
            product = get_object_or_404(Product, id=product_id)
            products = PersonalizationEngine.get_cross_sell_recommendations(product, limit)
        else:
            products = []
    elif recommendation_type == 'upsell':
        product_id = request.GET.get('product_id')
        if product_id:
            product = get_object_or_404(Product, id=product_id)
            products = PersonalizationEngine.get_upsell_recommendations(product, limit)
        else:
            products = []
    else:
        products = []
    
    # Serialize products
    products_data = []
    for product in products:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'image': product.image.url if product.image else None,
            'url': f"/product/{product.slug}/",
            'rating': getattr(product, 'average_rating', 0),
            'vendor': product.vendor.username if product.vendor else 'Vintage Store'
        })
    
    return JsonResponse({'products': products_data})


def track_email_open(request, user_id, campaign_id):
    """
    Track email opens for analytics
    """
    try:
        user = User.objects.get(id=user_id)
        profile = getattr(user, 'customer_profile', None)
        if profile:
            profile.email_opens += 1
            profile.save()
    except User.DoesNotExist:
        pass
    
    # Return 1x1 transparent pixel
    from django.http import HttpResponse
    import base64
    
    pixel = base64.b64decode('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7')
    return HttpResponse(pixel, content_type='image/gif')


def track_email_click(request, user_id, campaign_id):
    """
    Track email clicks for analytics
    """
    try:
        user = User.objects.get(id=user_id)
        profile = getattr(user, 'customer_profile', None)
        if profile:
            profile.email_clicks += 1
            profile.save()
    except User.DoesNotExist:
        pass
    
    # Redirect to intended URL
    redirect_url = request.GET.get('url', '/')
    from django.shortcuts import redirect
    return redirect(redirect_url)