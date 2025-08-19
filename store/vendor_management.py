"""
Advanced Vendor Management System for Vintage Ecommerce
Handles vendor onboarding, performance tracking, and commission management
"""

from django.db import models
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Avg, Count, Q, F
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal

from store.models import Product, Order, OrderItem, Review
from userauths.models import User


class VendorProfile(models.Model):
    """
    Extended vendor profile with business information
    """
    VERIFICATION_STATUS = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]
    
    BUSINESS_TYPES = [
        ('individual', 'Individual Seller'),
        ('small_business', 'Small Business'),
        ('corporation', 'Corporation'),
        ('non_profit', 'Non-Profit Organization'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    
    # Business Information
    business_name = models.CharField(max_length=200)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPES, default='individual')
    business_registration_number = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    
    # Contact Information
    business_phone = models.CharField(max_length=20)
    business_email = models.EmailField()
    business_address = models.TextField()
    business_city = models.CharField(max_length=100)
    business_state = models.CharField(max_length=100)
    business_country = models.CharField(max_length=100)
    business_postal_code = models.CharField(max_length=20)
    
    # Verification
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verification_date = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    
    # Documents
    business_license = models.FileField(upload_to='vendor_documents/', blank=True)
    tax_certificate = models.FileField(upload_to='vendor_documents/', blank=True)
    identity_document = models.FileField(upload_to='vendor_documents/', blank=True)
    
    # Performance Metrics
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_orders = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    response_time_hours = models.PositiveIntegerField(default=24)  # Average response time
    
    # Settings
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)  # Platform commission
    auto_approve_products = models.BooleanField(default=False)
    vacation_mode = models.BooleanField(default=False)
    vacation_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.business_name} ({self.user.username})"
    
    def update_performance_metrics(self):
        """Update vendor performance metrics"""
        orders = OrderItem.objects.filter(vendor=self.user, order__payment_status='Paid')
        
        self.total_orders = orders.count()
        self.total_sales = orders.aggregate(total=Sum('total'))['total'] or 0
        
        # Calculate average rating from product reviews
        reviews = Review.objects.filter(product__vendor=self.user)
        self.average_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        
        self.save(update_fields=['total_orders', 'total_sales', 'average_rating'])
    
    def get_commission_amount(self, order_total):
        """Calculate commission amount for an order"""
        return order_total * (self.commission_rate / 100)
    
    def is_verified(self):
        """Check if vendor is verified"""
        return self.verification_status == 'verified'


class VendorCommission(models.Model):
    """
    Track vendor commissions and payouts
    """
    COMMISSION_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('disputed', 'Disputed'),
    ]
    
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commissions')
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    order_item = models.ForeignKey('OrderItem', on_delete=models.CASCADE)
    
    # Commission Details
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)  # Order item total
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Platform commission %
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2)  # Platform fee
    net_amount = models.DecimalField(max_digits=12, decimal_places=2)  # Vendor payout
    
    # Status and Dates
    status = models.CharField(max_length=20, choices=COMMISSION_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Payment Details
    payment_method = models.CharField(max_length=50, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    payment_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.vendor.username} - {self.order.order_id} - ${self.net_amount}"


class VendorPerformanceMetrics(models.Model):
    """
    Track detailed vendor performance metrics
    """
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performance_metrics')
    date = models.DateField()
    
    # Sales Metrics
    orders_count = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    units_sold = models.PositiveIntegerField(default=0)
    
    # Customer Service Metrics
    response_time_avg = models.PositiveIntegerField(default=0)  # in hours
    customer_satisfaction = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    return_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Product Metrics
    products_added = models.PositiveIntegerField(default=0)
    products_updated = models.PositiveIntegerField(default=0)
    out_of_stock_products = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['vendor', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.vendor.username} - {self.date}"


class VendorNotification(models.Model):
    """
    Vendor-specific notifications
    """
    NOTIFICATION_TYPES = [
        ('new_order', 'New Order'),
        ('low_stock', 'Low Stock Alert'),
        ('payment_received', 'Payment Received'),
        ('product_review', 'New Product Review'),
        ('account_update', 'Account Update'),
        ('policy_update', 'Policy Update'),
        ('performance_alert', 'Performance Alert'),
    ]
    
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    action_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.vendor.username} - {self.title}"


class VendorManager:
    """
    Vendor management operations
    """
    
    @staticmethod
    def create_vendor_profile(user, business_data):
        """
        Create vendor profile with business information
        """
        profile = VendorProfile.objects.create(
            user=user,
            **business_data
        )
        
        # Send verification email
        VendorManager.send_verification_email(profile)
        
        return profile
    
    @staticmethod
    def verify_vendor(profile, approved=True, notes=""):
        """
        Verify or reject vendor application
        """
        if approved:
            profile.verification_status = 'verified'
            profile.verification_date = timezone.now()
            profile.verification_notes = notes
            profile.save()
            
            # Send approval email
            VendorManager.send_approval_email(profile)
            
            # Create welcome notification
            VendorNotification.objects.create(
                vendor=profile.user,
                notification_type='account_update',
                title='Welcome to Vintage Marketplace!',
                message='Your vendor account has been approved. You can now start selling on our platform.',
                action_url='/vendor/dashboard/'
            )
        else:
            profile.verification_status = 'rejected'
            profile.verification_notes = notes
            profile.save()
            
            # Send rejection email
            VendorManager.send_rejection_email(profile, notes)
    
    @staticmethod
    def calculate_vendor_commission(order_item):
        """
        Calculate and create commission record
        """
        vendor_profile = getattr(order_item.vendor, 'vendor_profile', None)
        if not vendor_profile:
            return None
        
        gross_amount = order_item.total
        commission_rate = vendor_profile.commission_rate
        commission_amount = gross_amount * (commission_rate / 100)
        net_amount = gross_amount - commission_amount
        
        commission = VendorCommission.objects.create(
            vendor=order_item.vendor,
            order=order_item.order,
            order_item=order_item,
            gross_amount=gross_amount,
            commission_rate=commission_rate,
            commission_amount=commission_amount,
            net_amount=net_amount
        )
        
        return commission
    
    @staticmethod
    def process_vendor_payout(vendor, amount, payment_method="bank_transfer"):
        """
        Process payout to vendor
        """
        # Get pending commissions
        pending_commissions = VendorCommission.objects.filter(
            vendor=vendor,
            status='approved'
        )
        
        total_pending = pending_commissions.aggregate(
            total=Sum('net_amount')
        )['total'] or 0
        
        if amount > total_pending:
            raise ValueError("Payout amount exceeds pending commissions")
        
        # Mark commissions as paid
        paid_amount = Decimal('0.00')
        for commission in pending_commissions:
            if paid_amount + commission.net_amount <= amount:
                commission.status = 'paid'
                commission.paid_at = timezone.now()
                commission.payment_method = payment_method
                commission.save()
                paid_amount += commission.net_amount
            
            if paid_amount >= amount:
                break
        
        # Create notification
        VendorNotification.objects.create(
            vendor=vendor,
            notification_type='payment_received',
            title=f'Payment Processed - ${paid_amount}',
            message=f'Your payout of ${paid_amount} has been processed via {payment_method}.',
        )
        
        return paid_amount
    
    @staticmethod
    def send_verification_email(profile):
        """
        Send vendor verification email
        """
        context = {
            'vendor': profile,
            'verification_url': f"{settings.SITE_URL}/admin/vendor/verify/{profile.id}/"
        }
        
        html_content = render_to_string('emails/vendor_verification_request.html', context)
        text_content = render_to_string('emails/vendor_verification_request.txt', context)
        
        send_mail(
            subject='Vendor Application Received - Vintage Marketplace',
            message=text_content,
            html_message=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
    
    @staticmethod
    def send_approval_email(profile):
        """
        Send vendor approval email
        """
        context = {
            'vendor': profile,
            'dashboard_url': f"{settings.SITE_URL}/vendor/dashboard/"
        }
        
        html_content = render_to_string('emails/vendor_approved.html', context)
        text_content = render_to_string('emails/vendor_approved.txt', context)
        
        send_mail(
            subject='Congratulations! Your Vendor Account is Approved',
            message=text_content,
            html_message=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[profile.business_email],
            fail_silently=False,
        )
    
    @staticmethod
    def send_rejection_email(profile, reason):
        """
        Send vendor rejection email
        """
        context = {
            'vendor': profile,
            'reason': reason,
            'reapply_url': f"{settings.SITE_URL}/vendor/apply/"
        }
        
        html_content = render_to_string('emails/vendor_rejected.html', context)
        text_content = render_to_string('emails/vendor_rejected.txt', context)
        
        send_mail(
            subject='Vendor Application Update - Vintage Marketplace',
            message=text_content,
            html_message=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[profile.business_email],
            fail_silently=False,
        )
    
    @staticmethod
    def get_vendor_analytics(vendor, days=30):
        """
        Get comprehensive vendor analytics
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Sales metrics
        orders = OrderItem.objects.filter(
            vendor=vendor,
            order__date__gte=start_date,
            order__payment_status='Paid'
        )
        
        total_revenue = orders.aggregate(total=Sum('total'))['total'] or 0
        total_orders = orders.count()
        total_units = orders.aggregate(total=Sum('qty'))['total'] or 0
        
        # Commission data
        commissions = VendorCommission.objects.filter(
            vendor=vendor,
            created_at__gte=start_date
        )
        
        total_commission = commissions.aggregate(total=Sum('commission_amount'))['total'] or 0
        net_earnings = commissions.aggregate(total=Sum('net_amount'))['total'] or 0
        
        # Product performance
        products = Product.objects.filter(vendor=vendor)
        top_products = products.annotate(
            revenue=Sum('orderitem__total', filter=Q(
                orderitem__order__date__gte=start_date,
                orderitem__order__payment_status='Paid'
            ))
        ).order_by('-revenue')[:5]
        
        # Customer metrics
        unique_customers = orders.values('order__customer').distinct().count()
        
        # Reviews
        reviews = Review.objects.filter(
            product__vendor=vendor,
            date__gte=start_date
        )
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        
        return {
            'total_revenue': float(total_revenue),
            'total_orders': total_orders,
            'total_units': total_units,
            'total_commission': float(total_commission),
            'net_earnings': float(net_earnings),
            'unique_customers': unique_customers,
            'avg_rating': float(avg_rating),
            'top_products': top_products,
            'review_count': reviews.count()
        }


# Views for vendor management
@login_required
def vendor_dashboard(request):
    """
    Main vendor dashboard
    """
    if not hasattr(request.user, 'vendor_profile'):
        messages.error(request, "You need to complete vendor registration first.")
        return redirect('vendor:register')
    
    profile = request.user.vendor_profile
    
    # Get analytics
    analytics = VendorManager.get_vendor_analytics(request.user)
    
    # Get recent orders
    recent_orders = OrderItem.objects.filter(
        vendor=request.user
    ).select_related('order', 'product').order_by('-order__date')[:10]
    
    # Get recent notifications
    notifications = VendorNotification.objects.filter(
        vendor=request.user,
        is_read=False
    )[:5]
    
    # Get pending commissions
    pending_commissions = VendorCommission.objects.filter(
        vendor=request.user,
        status='pending'
    )
    
    context = {
        'profile': profile,
        'analytics': analytics,
        'recent_orders': recent_orders,
        'notifications': notifications,
        'pending_commissions': pending_commissions,
    }
    
    return render(request, 'vendor/dashboard.html', context)


@login_required
def vendor_commission_report(request):
    """
    Vendor commission and earnings report
    """
    if not hasattr(request.user, 'vendor_profile'):
        return redirect('vendor:register')
    
    # Get commission data
    commissions = VendorCommission.objects.filter(vendor=request.user)
    
    # Filter by status if specified
    status_filter = request.GET.get('status')
    if status_filter:
        commissions = commissions.filter(status=status_filter)
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        commissions = commissions.filter(created_at__gte=start_date)
    if end_date:
        commissions = commissions.filter(created_at__lte=end_date)
    
    # Calculate totals
    totals = commissions.aggregate(
        total_gross=Sum('gross_amount'),
        total_commission=Sum('commission_amount'),
        total_net=Sum('net_amount')
    )
    
    context = {
        'commissions': commissions.order_by('-created_at'),
        'totals': totals,
        'status_filter': status_filter,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'vendor/commission_report.html', context)


# Signal handlers for automatic commission calculation
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=OrderItem)
def create_vendor_commission(sender, instance, created, **kwargs):
    """
    Automatically create commission record when order item is created
    """
    if created and instance.order.payment_status == 'Paid':
        VendorManager.calculate_vendor_commission(instance)


@receiver(post_save, sender=Order)
def update_order_commissions(sender, instance, **kwargs):
    """
    Update commission status when order payment status changes
    """
    if instance.payment_status == 'Paid':
        # Approve commissions for paid orders
        VendorCommission.objects.filter(
            order=instance,
            status='pending'
        ).update(
            status='approved',
            approved_at=timezone.now()
        )