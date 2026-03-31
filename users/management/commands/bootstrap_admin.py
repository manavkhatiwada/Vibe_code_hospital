from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from users.models import User


def _load_env_file(path: Path) -> dict:
    values = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


class Command(BaseCommand):
    help = "Create or update ADMIN user from .env (ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_USERNAME)."

    def handle(self, *args, **options):
        env_path = Path(settings.BASE_DIR) / ".env"
        env_values = _load_env_file(env_path)

        email = env_values.get("ADMIN_EMAIL")
        password = env_values.get("ADMIN_PASSWORD")
        username = env_values.get("ADMIN_USERNAME", "admin")

        if not email or not password:
            raise CommandError(
                "ADMIN_EMAIL and ADMIN_PASSWORD must be defined in .env"
            )

        user = User.objects.filter(email=email).first()
        created = False

        if not user:
            user = User.objects.filter(username=username).first()

        if not user:
            created = True
            user = User(email=email, username=username)

        user.username = username
        user.email = email
        user.role = "ADMIN"
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created admin user: {email}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated admin user: {email}"))
