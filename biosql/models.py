from typing import Any, TYPE_CHECKING

from django.db import models as m

if TYPE_CHECKING:
    from overview.models import Gene, GeneSearchHistory


class Taxon(m.Model):
    """biosql.taxon model."""

    objects: m.Manager

    class Meta:
        """Taxon model options."""

        managed = False
        db_table = 'biosql"."taxon'
        verbose_name_plural = "Taxons"

    taxon_id = m.IntegerField(primary_key=True)
    ncbi_taxon_id = m.IntegerField(null=True, unique=True)
    parent_taxon_id = m.IntegerField(null=True, db_index=True)
    node_rank = m.CharField(max_length=32, null=True)
    genetic_code = m.SmallIntegerField(null=True)
    mito_genetic_code = m.SmallIntegerField(null=True)
    left_value = m.IntegerField(null=True, unique=True)
    right_value = m.IntegerField(null=True, unique=True)

class TaxonName(m.Model):
    """biosql.taxon_name model."""

    objects: m.Manager

    class Meta:
        """Taxon model options."""

        managed = False
        db_table = 'biosql"."taxon_name'
        verbose_name_plural = "Taxon names"

        constraints = [
            m.UniqueConstraint(
                "taxon_id",
                "name",
                "name_class",
                name="taxon_name_name_name_class_taxon_id_key",
            ),
        ]


    taxon_id = m.ForeignKey(Taxon, on_delete=m.DO_NOTHING)
    name = m.TextField(null=True)
    name_class = m.CharField(max_length=32, null=True, db_index=True)


class Dbxref(m.Model):
    """biosql.dbxref non-managed model."""

    objects: m.Manager

    class Meta:
        """Dbxref model options."""

        managed = False
        db_table = 'biosql"."dbxref'
        verbose_name_plural = "DBXRefs"

        constraints = [
            m.UniqueConstraint(
                "accession",
                "dbname",
                "version",
                name="dbxref_accession_dbname_version_key",
            ),
        ]

    dbxref_id = m.AutoField(primary_key=True)
    dbname = m.CharField(max_length=40)
    accession = m.CharField(max_length=128)
    version = m.IntegerField()

    data: "Gene"  # matview with gene data
    search_history: "GeneSearchHistory"  # gene search counter

    # RelatedManager[genphen.models.GeneDrugResistanceAssociation]
    drug_resistance_associations: Any
