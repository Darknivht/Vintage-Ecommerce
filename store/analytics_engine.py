"""
Advanced Analytics Engine for Vintage Ecommerce
Provides comprehensive business intelligence and reporting
"""

from django.db import models
from django.db.models import Sum, Avg, Count, Q, F
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
import json
from collections import defaultdict

from store.models import Product, Order, OrderItem, Review, Category
from userauths.models import User


class AnalyticsEngine:
    """
    Comprehensive analytics engine for business intelligence
    """
    
    @staticmethod
    def get_sales_analytics(vendor=None, days=30):
        """
        Get comprehensive sales analytics
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Base queryset
        orders = Order.objects.filter(
            date__gte=start_date,
            payment_status='Paid'
        )
        
        if vendor:
            orders = orders.filter(orderitem__vendor=vendor).distinct()
        
        # Calculate metrics
        total_orders = orders.count()
        total_revenue = orders.aggregate(total=Sum('total'))['total'] or 0
        average_order_value = orders.aggregate(avg=Avg('total'))['avg'] or 0
        
        # Daily sales data for charts
        daily_sales = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            day_orders = orders.filter(date__date=date.date())
            daily_revenue = day_orders.aggregate(total=Sum('total'))['total'] or 0
            daily_sales.append({
                'date': date.strftime('%Y-%m-%d'),
                'revenue': float(daily_revenue),
                'orders': day_orders.count()
            })
        
        # Top selling products
        if vendor:
            top_products = Product.objects.filter(
                vendor=vendor,
                orderitem__order__date__gte=start_date,
                orderitem__order__payment_status='Paid'
            ).annotate(
                units_sold=Sum('orderitem__qty'),
                revenue=Sum('orderitem__total')
            ).order_by('-units_sold')[:10]
        else:
            top_products = Product.objects.filter(
                orderitem__order__date__gte=start_date,
                orderitem__order__payment_status='Paid'
            ).annotate(
                units_sold=Sum('orderitem__qty'),
                revenue=Sum('orderitem__total')
            ).order_by('-units_sold')[:10]
        
        # Customer analytics
        repeat_customers = orders.values('customer').annotate(
            order_count=Count('id')
        ).filter(order_count__gt=1).count()
        
        new_customers = orders.filter(
            customer__date_joined__gte=start_date
        ).values('customer').distinct().count()
        
        return {
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'average_order_value': float(average_order_value),
            'daily_sales': daily_sales,
            'top_products': top_products,
            'repeat_customers': repeat_customers,
            'new_customers': new_customers,
            'period_days': days
        }
    
    @staticmethod
    def get_product_performance(vendor=None, days=30):
        """
        Analyze product performance metrics
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        products = Product.objects.filter(status='Published')
        if vendor:
            products = products.filter(vendor=vendor)
        
        # Product performance metrics
        product_stats = []
        for product in products:
            # Sales data
            sales = OrderItem.objects.filter(
                product=product,
                order__date__gte=start_date,
                order__payment_status='Paid'
            )
            
            units_sold = sales.aggregate(total=Sum('qty'))['total'] or 0
            revenue = sales.aggregate(total=Sum('total'))['total'] or 0
            
            # Review data
            reviews = Review.objects.filter(product=product, date__gte=start_date)
            avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
            review_count = reviews.count()
            
            # Conversion rate (views to sales)
            views = getattr(product, 'view_count', 0)
            conversion_rate = (units_sold / views * 100) if views > 0 else 0
            
            product_stats.append({
                'product': product,
                'units_sold': units_sold,
                'revenue': float(revenue),
                'avg_rating': float(avg_rating),
                'review_count': review_count,
                'views': views,
                'conversion_rate': round(conversion_rate, 2),
                'stock_level': product.stock
            })
        
        # Sort by revenue
        product_stats.sort(key=lambda x: x['revenue'], reverse=True)
        
        return product_stats
    
    @staticmethod
    def get_customer_analytics(vendor=None, days=30):
        """
        Analyze customer behavior and demographics
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Base customer queryset
        customers = User.objects.filter(
            customer_orders__date__gte=start_date,
            customer_orders__payment_status='Paid'
        ).distinct()
        
        if vendor:
            customers = customers.filter(
                customer_orders__orderitem__vendor=vendor
            ).distinct()
        
        # Customer segmentation
        customer_segments = {
            'new': customers.filter(date_joined__gte=start_date).count(),
            'returning': customers.filter(date_joined__lt=start_date).count(),
            'vip': customers.annotate(
                total_spent=Sum('customer_orders__total')
            ).filter(total_spent__gte=1000).count()
        }
        
        # Geographic distribution (if address data available)
        geographic_data = customers.values(
            'customer_addresses__country'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Customer lifetime value
        clv_data = customers.annotate(
            total_orders=Count('customer_orders'),
            total_spent=Sum('customer_orders__total'),
            avg_order_value=Avg('customer_orders__total')
        ).order_by('-total_spent')[:20]
        
        return {
            'total_customers': customers.count(),
            'customer_segments': customer_segments,
            'geographic_data': list(geographic_data),
            'top_customers': clv_data
        }
    
    @staticmethod
    def get_category_performance(days=30):
        """
        Analyze category performance
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        categories = Category.objects.filter(type='product')
        
        category_stats = []
        for category in categories:
            # Sales data for category
            sales = OrderItem.objects.filter(
                product__category=category,
                order__date__gte=start_date,
                order__payment_status='Paid'
            )
            
            revenue = sales.aggregate(total=Sum('total'))['total'] or 0
            units_sold = sales.aggregate(total=Sum('qty'))['total'] or 0
            product_count = Product.objects.filter(
                category=category,
                status='Published'
            ).count()
            
            category_stats.append({
                'category': category,
                'revenue': float(revenue),
                'units_sold': units_sold,
                'product_count': product_count,
                'avg_revenue_per_product': float(revenue / product_count) if product_count > 0 else 0
            })
        
        # Sort by revenue
        category_stats.sort(key=lambda x: x['revenue'], reverse=True)
        
        return category_stats
    
    @staticmethod
    def get_vendor_comparison(days=30):
        """
        Compare vendor performance
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        vendors = User.objects.filter(
            vendor_products__orderitem__order__date__gte=start_date,
            vendor_products__orderitem__order__payment_status='Paid'
        ).distinct()
        
        vendor_stats = []
        for vendor in vendors:
            # Sales data
            sales = OrderItem.objects.filter(
                vendor=vendor,
                order__date__gte=start_date,
                order__payment_status='Paid'
            )
            
            revenue = sales.aggregate(total=Sum('total'))['total'] or 0
            orders = sales.values('order').distinct().count()
            products = Product.objects.filter(vendor=vendor, status='Published').count()
            
            # Average rating
            avg_rating = Review.objects.filter(
                product__vendor=vendor,
                date__gte=start_date
            ).aggregate(avg=Avg('rating'))['avg'] or 0
            
            vendor_stats.append({
                'vendor': vendor,
                'revenue': float(revenue),
                'orders': orders,
                'products': products,
                'avg_rating': float(avg_rating),
                'revenue_per_product': float(revenue / products) if products > 0 else 0
            })
        
        # Sort by revenue
        vendor_stats.sort(key=lambda x: x['revenue'], reverse=True)
        
        return vendor_stats
    
    @staticmethod
    def get_financial_summary(vendor=None, days=30):
        """
        Get comprehensive financial summary
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Base orders
        orders = Order.objects.filter(
            date__gte=start_date,
            payment_status='Paid'
        )
        
        if vendor:
            orders = orders.filter(orderitem__vendor=vendor).distinct()
        
        # Revenue calculations
        gross_revenue = orders.aggregate(total=Sum('total'))['total'] or 0
        
        # Platform fees (10% commission)
        platform_fees = gross_revenue * 0.10
        net_revenue = gross_revenue - platform_fees
        
        # Refunds and returns
        refunded_orders = orders.filter(order_status='Refunded')
        refund_amount = refunded_orders.aggregate(total=Sum('total'))['total'] or 0
        
        # Growth comparison (previous period)
        prev_start = start_date - timedelta(days=days)
        prev_orders = Order.objects.filter(
            date__gte=prev_start,
            date__lt=start_date,
            payment_status='Paid'
        )
        
        if vendor:
            prev_orders = prev_orders.filter(orderitem__vendor=vendor).distinct()
        
        prev_revenue = prev_orders.aggregate(total=Sum('total'))['total'] or 0
        growth_rate = ((gross_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        
        return {
            'gross_revenue': float(gross_revenue),
            'platform_fees': float(platform_fees),
            'net_revenue': float(net_revenue),
            'refund_amount': float(refund_amount),
            'growth_rate': round(growth_rate, 2),
            'total_orders': orders.count(),
            'average_order_value': float(gross_revenue / orders.count()) if orders.count() > 0 else 0
        }


# Views for analytics dashboards
@login_required
def admin_analytics_dashboard(request):
    """
    Comprehensive admin analytics dashboard
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    days = int(request.GET.get('days', 30))
    
    # Get all analytics
    sales_data = AnalyticsEngine.get_sales_analytics(days=days)
    customer_data = AnalyticsEngine.get_customer_analytics(days=days)
    category_data = AnalyticsEngine.get_category_performance(days=days)
    vendor_data = AnalyticsEngine.get_vendor_comparison(days=days)
    financial_data = AnalyticsEngine.get_financial_summary(days=days)
    
    context = {
        'sales_data': sales_data,
        'customer_data': customer_data,
        'category_data': category_data,
        'vendor_data': vendor_data,
        'financial_data': financial_data,
        'days': days
    }
    
    return render(request, 'admin/analytics_dashboard.html', context)


@login_required
def vendor_analytics_dashboard(request):
    """
    Vendor-specific analytics dashboard
    """
    if not hasattr(request.user, 'vendor_profile'):
        return JsonResponse({'error': 'Vendor access required'}, status=403)
    
    days = int(request.GET.get('days', 30))
    
    # Get vendor-specific analytics
    sales_data = AnalyticsEngine.get_sales_analytics(vendor=request.user, days=days)
    product_data = AnalyticsEngine.get_product_performance(vendor=request.user, days=days)
    customer_data = AnalyticsEngine.get_customer_analytics(vendor=request.user, days=days)
    financial_data = AnalyticsEngine.get_financial_summary(vendor=request.user, days=days)
    
    context = {
        'sales_data': sales_data,
        'product_data': product_data,
        'customer_data': customer_data,
        'financial_data': financial_data,
        'days': days
    }
    
    return render(request, 'vendor/analytics_dashboard.html', context)


@login_required
def analytics_api(request):
    """
    API endpoint for analytics data (for AJAX requests)
    """
    data_type = request.GET.get('type')
    days = int(request.GET.get('days', 30))
    vendor = request.user if hasattr(request.user, 'vendor_profile') else None
    
    if data_type == 'sales':
        data = AnalyticsEngine.get_sales_analytics(vendor=vendor, days=days)
    elif data_type == 'products':
        data = AnalyticsEngine.get_product_performance(vendor=vendor, days=days)
    elif data_type == 'customers':
        data = AnalyticsEngine.get_customer_analytics(vendor=vendor, days=days)
    elif data_type == 'categories':
        data = AnalyticsEngine.get_category_performance(days=days)
    elif data_type == 'financial':
        data = AnalyticsEngine.get_financial_summary(vendor=vendor, days=days)
    else:
        return JsonResponse({'error': 'Invalid data type'}, status=400)
    
    return JsonResponse(data, safe=False)


class ReportGenerator:
    """
    Generate various business reports
    """
    
    @staticmethod
    def generate_sales_report(vendor=None, start_date=None, end_date=None):
        """
        Generate comprehensive sales report
        """
        if not start_date:
            start_date = timezone.now() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now()
        
        orders = Order.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            payment_status='Paid'
        )
        
        if vendor:
            orders = orders.filter(orderitem__vendor=vendor).distinct()
        
        report_data = {
            'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            'total_orders': orders.count(),
            'total_revenue': float(orders.aggregate(total=Sum('total'))['total'] or 0),
            'average_order_value': float(orders.aggregate(avg=Avg('total'))['avg'] or 0),
            'orders': []
        }
        
        for order in orders:
            report_data['orders'].append({
                'order_id': order.order_id,
                'customer': order.customer.username,
                'date': order.date.strftime('%Y-%m-%d %H:%M'),
                'total': float(order.total),
                'status': order.order_status,
                'payment_method': order.payment_method
            })
        
        return report_data
    
    @staticmethod
    def generate_inventory_report(vendor=None):
        """
        Generate inventory status report
        """
        products = Product.objects.filter(status='Published')
        if vendor:
            products = products.filter(vendor=vendor)
        
        report_data = {
            'total_products': products.count(),
            'low_stock_products': products.filter(stock__lte=10).count(),
            'out_of_stock_products': products.filter(stock=0).count(),
            'total_stock_value': sum(float(p.price) * p.stock for p in products),
            'products': []
        }
        
        for product in products:
            report_data['products'].append({
                'name': product.name,
                'sku': getattr(product, 'sku', 'N/A'),
                'category': product.category.title if product.category else 'N/A',
                'stock': product.stock,
                'price': float(product.price),
                'stock_value': float(product.price) * product.stock,
                'status': 'Out of Stock' if product.stock == 0 else 'Low Stock' if product.stock <= 10 else 'In Stock'
            })
        
        return report_data