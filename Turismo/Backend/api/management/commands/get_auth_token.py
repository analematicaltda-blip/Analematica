from django.core.management.base import BaseCommand, CommandError
from api.models import CustomUser
from rest_framework.authtoken.models import Token

class Command(BaseCommand):
    help = 'Retrieves the authentication token for a specific user.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='The username of the user to get the token for.')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = CustomUser.objects.get(username=username)
            token, created = Token.objects.get_or_create(user=user)
            if created:
                self.stdout.write(self.style.SUCCESS(f"New token created for user '{username}'."))
            self.stdout.write(self.style.SUCCESS(f"Auth Token: {token.key}"))
        except CustomUser.DoesNotExist:
            raise CommandError(f"User with username '{username}' does not exist.")
        except Exception as e:
            raise CommandError(f"An error occurred: {e}")