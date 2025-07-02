from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = 'Re-save all ImageFields/FileFields to trigger upload to Cloudinary'

    def handle(self, *args, **options):
        total = 0
        for model in apps.get_models():
            fields = [f for f in model._meta.fields if f.get_internal_type() in ["ImageField", "FileField"]]
            if not fields:
                continue

            for obj in model.objects.all():
                updated = False
                for field in fields:
                    file = getattr(obj, field.name)
                    if file and not file.name.startswith("http"):
                        # Re-save the field to trigger storage backend
                        setattr(obj, field.name, file)
                        updated = True
                if updated:
                    obj.save()
                    total += 1

        self.stdout.write(self.style.SUCCESS(f"Synced {total} objects' media to Cloudinary."))