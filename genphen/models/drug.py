from typing import Any

from django.db import models as m


class Drug(m.Model):
    """Drug non-managed model."""

    objects: m.Manager

    drug_id = m.AutoField(primary_key=True)
    drug_name = m.CharField(max_length=8_192, unique=True)
    # preferred drug code
    drug_code = m.CharField(max_length=8_192, unique=True)

    synonyms: Any  # RelatedManager[DrugSynonym]
    mic_tests: Any  # RelatedManager[MICTest]
    pds_tests: Any  # RelatedManager[PDSTest]
    gene_resistance_associations: Any  # RelatedManager[GeneDrugResistanceAssociation]
    variant_grades: Any  # RelatedManager[VariantGrade]
