from django.db.models import Subquery, PositiveIntegerField


class SubqueryCount(Subquery):  # pylint: disable=abstract-method
    """Simple count helper to annotate multiple counts in subqueries."""

    template = "(SELECT count(*) FROM (%(subquery)s) _count)"
    output_field = PositiveIntegerField()
