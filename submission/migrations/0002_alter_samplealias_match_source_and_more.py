# Generated by Django 4.1.5 on 2023-04-19 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="samplealias",
            name="match_source",
            field=models.CharField(
                choices=[
                    ("NO_MATCH", "No match found"),
                    ("FASTQ_UPLOADED", "Uploaded FASTQ file"),
                    ("FASTQ_UPLOADED_NEW_SAMPLE", "Uploaded FASTQ file, new sample"),
                    ("FASTQ_EXISTING", "Existing FASTQ file"),
                    ("NCBI", "NCBI sample name"),
                    ("NCBI_FASTQ", "NCBI accession keys"),
                    ("USER_ALIAS", "Existing user alias"),
                ],
                max_length=64,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="sequencingdata",
            name="data_location",
            field=models.CharField(
                choices=[("NCBI", "Ncbi"), ("TB-Kb", "Tbkb")],
                max_length=8192,
            ),
        ),
    ]