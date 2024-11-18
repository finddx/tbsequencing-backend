from django.db import models as m


class VariantToAnnotation(m.Model):
    """Variants to annotations M2M model."""

    objects: m.Manager

    variant = m.ForeignKey("Variant", on_delete=m.CASCADE)
    annotation = m.ForeignKey("Annotation", on_delete=m.CASCADE)

    class Meta:
        """VariantToAnnotation model options."""

        constraints = [
            m.UniqueConstraint(
                "variant",
                "annotation",
                name="varianttoannotation_va_an_key",
            ),
        ]
