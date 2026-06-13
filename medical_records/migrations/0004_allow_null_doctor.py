from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("medical_records", "0003_is_private"),
    ]

    operations = [
        migrations.AlterField(
            model_name="medicalrecord",
            name="doctor",
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to="doctors.doctor"),
        ),
    ]