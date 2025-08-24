from django.core.management.base import BaseCommand
from django.db import transaction
from userauths.models import User, Profile
from vendor.models import Vendor


class Command(BaseCommand):
    help = 'Fix existing vendor users by setting their user_type correctly'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Find all users who have vendor profiles but might not have user_type set
            vendor_profiles = Vendor.objects.all()
            
            fixed_count = 0
            created_profiles = 0
            
            for vendor in vendor_profiles:
                user = vendor.user
                
                # Get or create user profile
                profile, created = Profile.objects.get_or_create(
                    user=user,
                    defaults={
                        'user_type': 'Vendor',
                        'full_name': user.first_name + ' ' + user.last_name if user.first_name else user.username,
                    }
                )
                
                if created:
                    created_profiles += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created profile for vendor: {user.email}')
                    )
                
                # Update user_type if it's not set to Vendor
                if profile.user_type != 'Vendor':
                    profile.user_type = 'Vendor'
                    profile.save()
                    fixed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Fixed user_type for vendor: {user.email}')
                    )
            
            # Also check if there are users who created products but don't have vendor profiles
            from store.models import Product
            
            # Find users who have products but no vendor profile
            product_owners = User.objects.filter(
                product__isnull=False
            ).distinct()
            
            for user in product_owners:
                # Check if they have a vendor profile
                if not hasattr(user, 'vendor'):
                    # Create vendor profile
                    Vendor.objects.create(user=user, store_name=f"{user.username}'s Store")
                    self.stdout.write(
                        self.style.WARNING(f'Created missing VendorProfile for: {user.email}')
                    )
                
                # Ensure their Profile has correct user_type
                profile, created = Profile.objects.get_or_create(
                    user=user,
                    defaults={
                        'user_type': 'Vendor',
                        'full_name': user.first_name + ' ' + user.last_name if user.first_name else user.username,
                    }
                )
                
                if created:
                    created_profiles += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created profile for product owner: {user.email}')
                    )
                
                if profile.user_type != 'Vendor':
                    profile.user_type = 'Vendor'
                    profile.save()
                    fixed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Fixed user_type for product owner: {user.email}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully processed vendor users. Fixed: {fixed_count}, Created profiles: {created_profiles}'
                )
            )