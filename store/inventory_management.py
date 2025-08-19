"""
Advanced Inventory Management System for Vintage Ecommerce
Handles stock tracking, low stock alerts, and automated reordering
"""

from django.db import models, transaction
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

from store.models import Product, OrderItem
from userauths.models import User


class InventoryAlert(models.Model):
    """Model to track inventory alerts"""
    ALERT_TYPES = [
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('reorder_point', 'Reorder Point Reached'),
        ('overstock', 'Overstock Alert'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.get_alert_type_display()}"


class StockMovement(models.Model):
    """Track all stock movements for audit trail"""
    MOVEMENT_TYPES = [
        ('purchase', 'Purchase/Restock'),
        ('sale', 'Sale'),
        ('return', 'Return'),
        ('adjustment', 'Manual Adjustment'),
        ('damage', 'Damage/Loss'),
        ('transfer', 'Transfer'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()  # Positive for inbound, negative for outbound
    previous_stock = models.PositiveIntegerField()
    new_stock = models.PositiveIntegerField()
    reference = models.CharField(max_length=100, blank=True)  # Order ID, etc.
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.movement_type} ({self.quantity})"


class InventoryManager:
    """Advanced inventory management operations"""
    
    @staticmethod
    def update_stock(product, quantity_change, movement_type, reference="", notes="", user=None):
        """
        Update product stock with full audit trail
        """
        with transaction.atomic():
            # Get current stock
            previous_stock = product.stock
            new_stock = max(0, previous_stock + quantity_change)
            
            # Update product stock
            product.stock = new_stock
            product.save(update_fields=['stock'])
            
            # Create stock movement record
            StockMovement.objects.create(
                product=product,
                movement_type=movement_type,
                quantity=quantity_change,
                previous_stock=previous_stock,
                new_stock=new_stock,
                reference=reference,
                notes=notes,
                created_by=user
            )
            
            # Check for alerts
            InventoryManager.check_stock_alerts(product)
            
            return new_stock
    
    @staticmethod
    def check_stock_alerts(product):
        """
        Check and create inventory alerts based on stock levels
        """
        current_stock = product.stock
        
        # Define thresholds (can be made configurable per product)
        low_stock_threshold = getattr(product, 'low_stock_threshold', 10)
        reorder_point = getattr(product, 'reorder_point', 5)
        
        # Clear existing unresolved alerts for this product
        InventoryAlert.objects.filter(
            product=product,
            is_resolved=False
        ).update(is_resolved=True, resolved_at=timezone.now())
        
        # Check for out of stock
        if current_stock == 0:
            InventoryAlert.objects.create(
                product=product,
                alert_type='out_of_stock',
                message=f"{product.name} is out of stock!"
            )
            InventoryManager.send_stock_alert_email(product, 'out_of_stock')
        
        # Check for low stock
        elif current_stock <= low_stock_threshold:
            InventoryAlert.objects.create(
                product=product,
                alert_type='low_stock',
                message=f"{product.name} stock is low ({current_stock} remaining)"
            )
            InventoryManager.send_stock_alert_email(product, 'low_stock')
        
        # Check for reorder point
        elif current_stock <= reorder_point:
            InventoryAlert.objects.create(
                product=product,
                alert_type='reorder_point',
                message=f"{product.name} has reached reorder point ({current_stock} remaining)"
            )
    
    @staticmethod
    def send_stock_alert_email(product, alert_type):
        """
        Send email alerts for stock issues
        """
        if not product.vendor or not product.vendor.email:
            return
        
        subject_map = {
            'out_of_stock': f'URGENT: {product.name} is Out of Stock',
            'low_stock': f'Alert: {product.name} Stock is Low',
            'reorder_point': f'Reorder Alert: {product.name}'
        }
        
        message_map = {
            'out_of_stock': f'Your product "{product.name}" is completely out of stock. Please restock immediately to avoid lost sales.',
            'low_stock': f'Your product "{product.name}" stock is running low ({product.stock} remaining). Consider restocking soon.',
            'reorder_point': f'Your product "{product.name}" has reached the reorder point ({product.stock} remaining). Time to reorder!'
        }
        
        try:
            send_mail(
                subject=subject_map.get(alert_type, 'Stock Alert'),
                message=message_map.get(alert_type, 'Stock alert for your product.'),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[product.vendor.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send stock alert email: {e}")
    
    @staticmethod
    def get_inventory_analytics(vendor=None, days=30):
        """
        Get comprehensive inventory analytics
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Base queryset
        products = Product.objects.all()
        if vendor:
            products = products.filter(vendor=vendor)
        
        # Stock movements in period
        movements = StockMovement.objects.filter(
            created_at__gte=start_date,
            product__in=products
        )
        
        # Calculate metrics
        total_products = products.count()
        low_stock_products = products.filter(stock__lte=10).count()
        out_of_stock_products = products.filter(stock=0).count()
        
        # Sales analytics
        sales_movements = movements.filter(movement_type='sale')
        total_units_sold = abs(sum(m.quantity for m in sales_movements))
        
        # Top selling products
        top_selling = products.annotate(
            units_sold=models.Sum(
                models.Case(
                    models.When(
                        stock_movements__movement_type='sale',
                        stock_movements__created_at__gte=start_date,
                        then=models.F('stock_movements__quantity') * -1
                    ),
                    default=0,
                    output_field=models.IntegerField()
                )
            )
        ).order_by('-units_sold')[:10]
        
        # Slow moving products (no sales in period)
        slow_moving = products.exclude(
            stock_movements__movement_type='sale',
            stock_movements__created_at__gte=start_date
        ).filter(stock__gt=0)[:10]
        
        return {
            'total_products': total_products,
            'low_stock_products': low_stock_products,
            'out_of_stock_products': out_of_stock_products,
            'total_units_sold': total_units_sold,
            'top_selling': top_selling,
            'slow_moving': slow_moving,
            'stock_value': sum(p.price * p.stock for p in products),
            'period_days': days
        }


# Views for inventory management
@login_required
def inventory_dashboard(request):
    """
    Inventory management dashboard for vendors
    """
    if not hasattr(request.user, 'vendor_profile'):
        messages.error(request, "Access denied. Vendor account required.")
        return redirect('store:index')
    
    # Get vendor's products
    products = Product.objects.filter(vendor=request.user).select_related('category')
    
    # Get recent alerts
    recent_alerts = InventoryAlert.objects.filter(
        product__vendor=request.user,
        is_resolved=False
    )[:10]
    
    # Get analytics
    analytics = InventoryManager.get_inventory_analytics(vendor=request.user)
    
    # Get recent stock movements
    recent_movements = StockMovement.objects.filter(
        product__vendor=request.user
    )[:20]
    
    context = {
        'products': products,
        'recent_alerts': recent_alerts,
        'analytics': analytics,
        'recent_movements': recent_movements,
    }
    
    return render(request, 'vendor/inventory_dashboard.html', context)


@login_required
def update_product_stock(request):
    """
    AJAX endpoint to update product stock
    """
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        new_stock = request.POST.get('stock')
        notes = request.POST.get('notes', '')
        
        try:
            product = get_object_or_404(Product, id=product_id, vendor=request.user)
            old_stock = product.stock
            stock_change = int(new_stock) - old_stock
            
            InventoryManager.update_stock(
                product=product,
                quantity_change=stock_change,
                movement_type='adjustment',
                notes=notes,
                user=request.user
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Stock updated successfully. Changed from {old_stock} to {new_stock}',
                'new_stock': product.stock
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating stock: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def resolve_inventory_alert(request, alert_id):
    """
    Mark inventory alert as resolved
    """
    try:
        alert = get_object_or_404(
            InventoryAlert,
            id=alert_id,
            product__vendor=request.user
        )
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.save()
        
        messages.success(request, 'Alert resolved successfully.')
    except Exception as e:
        messages.error(request, f'Error resolving alert: {str(e)}')
    
    return redirect('store:inventory_dashboard')


# Signal handlers to automatically track stock movements
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=OrderItem)
def track_sale_stock_movement(sender, instance, created, **kwargs):
    """
    Automatically create stock movement when order item is created
    """
    if created:
        InventoryManager.update_stock(
            product=instance.product,
            quantity_change=-instance.qty,
            movement_type='sale',
            reference=f"Order #{instance.order.order_id}",
            notes=f"Sale to {instance.order.customer.username}"
        )