"""
Comprehensive Email Service for Vintage Ecommerce
Handles all email notifications with beautiful HTML templates
"""

import os
import logging
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string, get_template
from django.utils.html import strip_tags
from django.urls import reverse
from decimal import Decimal

logger = logging.getLogger(__name__)

class EmailService:
    """
    Centralized email service for all email notifications
    """
    
    def __init__(self):
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@vintage-ecommerce.com')
        self.site_name = getattr(settings, 'SITE_NAME', "Vintage Ecommerce")
        self.site_url = getattr(settings, 'SITE_URL', "http://localhost:8000")
    
    def _send_email(
        self, 
        template_name: str, 
        context: Dict[str, Any], 
        to_emails: List[str], 
        subject: str,
        attachments: Optional[List] = None
    ) -> bool:
        """
        Generic method to send HTML emails with templates
        """
        try:
            # Add common context variables
            context.update({
                'site_name': self.site_name,
                'site_url': self.site_url,
                'support_email': self.from_email,
            })
            
            # Render HTML content
            html_content = render_to_string(f'emails/{template_name}.html', context)
            
            # Create plain text version
            text_content = strip_tags(html_content)
            
            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=to_emails,
            )
            
            email.attach_alternative(html_content, "text/html")
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    email.attach_file(attachment)
            
            # Send email
            email.send()
            logger.info(f"Email sent successfully to {to_emails}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_emails}: {str(e)}")
            return False
    
    # Order related emails
    def send_order_confirmation(self, order, user_email: str) -> bool:
        """Send order confirmation email"""
        context = {
            'order': order,
            'user': order.user,
            'order_items': order.orderitem_set.all(),
            'order_url': f"{self.site_url}/customer/order/{order.oid}/",
        }
        
        return self._send_email(
            template_name='order_confirmation',
            context=context,
            to_emails=[user_email],
            subject=f'Order Confirmation - #{order.oid}'
        )
    
    def send_new_order_to_vendor(self, order, vendor) -> bool:
        """Send new order notification to vendor"""
        # Get vendor's items in this order
        vendor_items = order.orderitem_set.filter(vendor=vendor)
        vendor_total = sum(item.total for item in vendor_items)
        
        context = {
            'order': order,
            'vendor': vendor,
            'vendor_items': vendor_items,
            'vendor_total': vendor_total,
            'vendor_dashboard_url': f"{self.site_url}/vendor/dashboard/",
        }
        
        return self._send_email(
            template_name='vendor_new_order',
            context=context,
            to_emails=[vendor.email],
            subject=f'New Order #{order.oid} - Action Required'
        )
    
    def send_order_shipped(self, order, tracking_number: str = None) -> bool:
        """Send order shipped notification"""
        context = {
            'order': order,
            'user': order.user,
            'tracking_number': tracking_number,
            'order_url': f"{self.site_url}/customer/order/{order.oid}/",
        }
        
        return self._send_email(
            template_name='order_shipped',
            context=context,
            to_emails=[order.user.email],
            subject=f'Your Order Has Been Shipped - #{order.oid}'
        )
    
    def send_order_delivered(self, order) -> bool:
        """Send order delivered notification"""
        context = {
            'order': order,
            'user': order.user,
            'order_url': f"{self.site_url}/customer/order/{order.oid}/",
            'review_url': f"{self.site_url}/customer/order/{order.oid}/review/",
        }
        
        return self._send_email(
            template_name='order_delivered',
            context=context,
            to_emails=[order.user.email],
            subject=f'Order Delivered - #{order.oid}'
        )
    
    # User account emails
    def send_welcome_email(self, user) -> bool:
        """Send welcome email to new users"""
        context = {
            'user': user,
            'login_url': f"{self.site_url}/auth/sign-in/",
            'shop_url': f"{self.site_url}/shop/",
        }
        
        return self._send_email(
            template_name='welcome',
            context=context,
            to_emails=[user.email],
            subject=f'Welcome to {self.site_name}!'
        )
    
    def send_password_reset_email(self, user, reset_url: str) -> bool:
        """Send password reset email"""
        context = {
            'user': user,
            'reset_url': reset_url,
        }
        
        return self._send_email(
            template_name='password_reset',
            context=context,
            to_emails=[user.email],
            subject='Password Reset Request'
        )
    
    # Vendor related emails
    def send_new_order_to_vendor(self, order, vendor) -> bool:
        """Send new order notification to vendor"""
        vendor_items = order.orderitem_set.filter(product__vendor=vendor)
        
        context = {
            'order': order,
            'vendor': vendor,
            'vendor_items': vendor_items,
            'vendor_dashboard_url': f"{self.site_url}/vendor/dashboard/",
        }
        
        return self._send_email(
            template_name='vendor_new_order',
            context=context,
            to_emails=[vendor.email],
            subject=f'New Order Received - #{order.oid}'
        )
    
    def send_payout_notification(self, vendor, amount: Decimal, order) -> bool:
        """Send payout notification to vendor"""
        context = {
            'vendor': vendor,
            'amount': amount,
            'order': order,
            'payout_date': order.date,
        }
        
        return self._send_email(
            template_name='vendor_payout',
            context=context,
            to_emails=[vendor.email],
            subject=f'Payout Notification - ₦{amount}'
        )
    
    # Product related emails
    def send_product_approved(self, product, vendor) -> bool:
        """Send product approval notification to vendor"""
        context = {
            'product': product,
            'vendor': vendor,
            'product_url': f"{self.site_url}/product/{product.slug}/",
        }
        
        return self._send_email(
            template_name='product_approved',
            context=context,
            to_emails=[vendor.email],
            subject=f'Product Approved - {product.name}'
        )
    
    def send_product_rejected(self, product, vendor, reason: str) -> bool:
        """Send product rejection notification to vendor"""
        context = {
            'product': product,
            'vendor': vendor,
            'reason': reason,
            'vendor_dashboard_url': f"{self.site_url}/vendor/dashboard/",
        }
        
        return self._send_email(
            template_name='product_rejected',
            context=context,
            to_emails=[vendor.email],
            subject=f'Product Rejected - {product.name}'
        )
    
    def send_low_stock_alert(self, product, vendor) -> bool:
        """Send low stock alert to vendor"""
        context = {
            'product': product,
            'vendor': vendor,
            'current_stock': product.stock,
            'vendor_dashboard_url': f"{self.site_url}/vendor/dashboard/",
        }
        
        return self._send_email(
            template_name='low_stock_alert',
            context=context,
            to_emails=[vendor.email],
            subject=f'Low Stock Alert - {product.name}'
        )
    
    # Review related emails
    def send_review_notification(self, review, vendor) -> bool:
        """Send new review notification to vendor"""
        context = {
            'review': review,
            'product': review.product,
            'vendor': vendor,
            'customer': review.user,
            'product_url': f"{self.site_url}/product/{review.product.slug}/",
        }
        
        return self._send_email(
            template_name='new_review',
            context=context,
            to_emails=[vendor.email],
            subject=f'New Review for {review.product.name}'
        )
    
    # Newsletter and promotional emails
    def send_newsletter(self, subscribers: List[str], subject: str, content: str) -> bool:
        """Send newsletter to subscribers"""
        context = {
            'content': content,
            'unsubscribe_url': f"{self.site_url}/newsletter/unsubscribe/",
        }
        
        return self._send_email(
            template_name='newsletter',
            context=context,
            to_emails=subscribers,
            subject=subject
        )
    
    def send_promotional_email(self, user, promotion_data: Dict) -> bool:
        """Send promotional email"""
        context = {
            'user': user,
            'promotion': promotion_data,
            'shop_url': f"{self.site_url}/shop/",
        }
        
        return self._send_email(
            template_name='promotion',
            context=context,
            to_emails=[user.email],
            subject=promotion_data.get('subject', 'Special Offer for You!')
        )
    
    # Customer service emails
    def send_contact_confirmation(self, name: str, email: str, message: str) -> bool:
        """Send contact form confirmation"""
        context = {
            'name': name,
            'message': message,
            'contact_url': f"{self.site_url}/contact/",
        }
        
        return self._send_email(
            template_name='contact_confirmation',
            context=context,
            to_emails=[email],
            subject='We Received Your Message'
        )
    
    def send_support_ticket(self, user, ticket_data: Dict) -> bool:
        """Send support ticket confirmation"""
        context = {
            'user': user,
            'ticket': ticket_data,
            'ticket_id': ticket_data.get('id'),
        }
        
        return self._send_email(
            template_name='support_ticket',
            context=context,
            to_emails=[user.email],
            subject=f'Support Ticket Created - #{ticket_data.get("id")}'
        )

# Create global instance
email_service = EmailService()