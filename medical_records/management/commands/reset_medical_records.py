from pathlib import Path
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand

from medical_records.models import MedicalRecord


class Command(BaseCommand):
    help = "Delete all medical records and their uploaded files from the database and media folder."

    def handle(self, *args, **options):
        media_root = Path(settings.MEDIA_ROOT)
        records_root = media_root / "medical_reports"

        deleted_rows = MedicalRecord.objects.count()
        deleted_files = 0

        for record in MedicalRecord.objects.exclude(report_file=""):
            if record.report_file and record.report_file.name:
                file_path = media_root / record.report_file.name
                if file_path.exists():
                    file_path.unlink()
                    deleted_files += 1

        MedicalRecord.objects.all().delete()

        if records_root.exists():
            shutil.rmtree(records_root)
        records_root.mkdir(parents=True, exist_ok=True)

        self.stdout.write(self.style.SUCCESS(
            f"Deleted {deleted_rows} medical record rows and {deleted_files} uploaded files."
        ))