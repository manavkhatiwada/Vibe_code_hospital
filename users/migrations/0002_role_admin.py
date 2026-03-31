from django.db import migrations, models


def migrate_hospital_role_to_admin(apps, schema_editor):
    User = apps.get_model("users", "User")
    User.objects.filter(role="HOSPITAL").update(role="ADMIN")


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(migrate_hospital_role_to_admin, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[("PATIENT", "patient"), ("DOCTOR", "doctor"), ("ADMIN", "admin")],
                max_length=20,
            ),
        ),
    ]
