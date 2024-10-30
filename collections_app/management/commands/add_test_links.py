from django.core.management.base import BaseCommand
from collections_app.models import Collection, Link

class Command(BaseCommand):
    help = 'Adds 559 test links to a specified collection'

    def add_arguments(self, parser):
        parser.add_argument('collection_id', type=int, help='ID of the collection to add links to')

    def handle(self, *args, **options):
        collection_id = options['collection_id']
        try:
            collection = Collection.objects.get(id=collection_id)
        except Collection.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Collection with id {collection_id} does not exist'))
            return

        links_to_create = []
        for _ in range(559):
            links_to_create.append(Link(
                collection=collection,
                name="Keeplinker",
                url="https://keeplinker.com/",
                description="Test link for pagination"
            ))

        Link.objects.bulk_create(links_to_create)

        self.stdout.write(self.style.SUCCESS(f'Successfully added 559 test links to collection {collection_id}'))