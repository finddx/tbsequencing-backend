# Generated by Django 4.1.5 on 2023-04-21 11:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("genphen", "0003_variantgrade_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="genedrugresistanceassociation",
            name="drug",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="gene_resistance_associations",
                to="genphen.drug",
            ),
        ),
    ]