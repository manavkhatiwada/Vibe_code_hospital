from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('doctors', '0004_alter_doctor_specialization_and_more'),
        ('hospitals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='hospital',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='hospitals.hospital',
            ),
        ),
    ]
