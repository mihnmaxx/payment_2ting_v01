from django.core.management.base import BaseCommand
from orders.services import FirebirdListener

class Command(BaseCommand):
    help = 'Start listening to Firebird database for new orders'

    def handle(self, *args, **options):
        listener = FirebirdListener()
        self.stdout.write('Starting Firebird listener...')
        listener.listen()
