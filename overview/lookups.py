from django.db.models import Lookup


class Overlaps(Lookup):  # pylint: disable=abstract-method
    """Check if a DateRange value has common points with other DateRange value."""

    lookup_name = "overlaps"

    def as_sql(self, compiler, connection):
        """Make use of "&&" daterange overlap operator."""
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        # pylint: disable=consider-using-f-string
        return (
            "%s && %s" % (lhs, rhs),
            params,
        )
