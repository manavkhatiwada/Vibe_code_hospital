from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctors', '0004_alter_doctor_specialization_and_more'),
        ('medical_records', '0004_allow_null_doctor'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalrecord',
            name='shared_with',
            field=models.ManyToManyField(blank=True, help_text='Doctors the patient explicitly shared this private record with.', related_name='shared_records', to='doctors.doctor'),
        ),
    ]
