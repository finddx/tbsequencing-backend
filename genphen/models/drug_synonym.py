from django.db import models as m

from .drug import Drug


class DrugSynonym(m.Model):
    """Drug synonym non-managed model."""

    objects: m.Manager

    class CodeType(m.TextChoices):
        """Drug synonym code types."""

        THREE_LETTER = "three_letter_code", "Three letter code"
        # TODO add other drug synonym code types

    drug_name_synonym = m.CharField(max_length=128, unique=True)
    drug = m.ForeignKey(Drug, on_delete=m.CASCADE, related_name="synonyms")
    code = m.CharField(max_length=128, choices=CodeType.choices, null=True)
