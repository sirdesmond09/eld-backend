from django.core.management.base import BaseCommand
from core.models.accounts.user import User


class Command(BaseCommand):
    help = 'Verify all existing users'

    def handle(self, *args, **options):
        # Get all users that are not verified
        unverified_users = User.objects.filter(is_email_verified=False)
        
        if unverified_users.exists():
            self.stdout.write(f'Found {unverified_users.count()} unverified users')
            
            # Verify all users
            for user in unverified_users:
                user.is_email_verified = True
                user.is_active = True
                user.save()
                self.stdout.write(f'Verified user: {user.email}')
            
            self.stdout.write(
                self.style.SUCCESS('Successfully verified all users')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('All users are already verified')
            ) 