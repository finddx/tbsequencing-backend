from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db import connection

from identity.models import User

TEST_USERS = {
    "user": {"first_name": "User", "last_name": "Name", "password": "123123"},
    "alice": {"first_name": "Alice", "last_name": "Baxter", "password": "123123"},
    "john": {"first_name": "John", "last_name": "Tailor", "password": "123123"},
    "admin": {"is_superuser": True, "is_staff": True, "password": "123123"},
}


class Command(BaseCommand):
    """
    Perform any necessary post-migration tasks.

    Such as creating default users and packages for non-prod env,
    generating big amounts of fake data also for non-prod env (if --full flag specified).
    """

    requires_migrations_checks = True

    def add_arguments(self, parser):
        """Add arguments to the command."""
        parser.add_argument(
            "--full",
            action="store_true",
            help="Perform full sample loading. If invoked, --amount and --limit are in action",
        )
        parser.add_argument(
            "--amount",
            action="store",
            type=int,
            default=10_000,
            help="how many records of each model should be generated in one run "
            "(recommended to be multiple of 10k)",
        )
        parser.add_argument(
            "--limit",
            action="store",
            type=int,
            default=1_000_000,
            help="up to which amount of records should be generated for each model",
        )

    def handle(self, *args, **options):
        """
        Perform any necessary post-migrate routine.

        Such as updating search_path
        (because we don't want to do that inside migrations).
        """
        # pylint: disable=too-many-locals, too-many-branches, too-many-statements

        print(
            f"Updating django site "
            f"with domain {settings.FRONTEND_DOMAIN} "
            f"and name {settings.SITE_NAME}",
        )

        site: Site = Site.objects.get_current()
        site.domain = settings.FRONTEND_DOMAIN
        site.name = settings.SITE_NAME
        site.save()

        db_user = settings.DATABASES["default"]["USER"]
        db_name = settings.DATABASES["default"]["NAME"]
        search_path = "public,genphensql,biosql"

        print(f"Updating search path for {db_user} in {db_name}: {search_path}")
        with connection.cursor() as cursor:
            cursor.execute(
                f"ALTER ROLE {db_user} IN DATABASE {db_name} "
                f"SET search_path TO {search_path}",
            )

        # create 3 test users for non-prod envs
        if not settings.IS_PRODUCTION:
            for username, props in TEST_USERS.items():
                props["email"] = f"{username}@example.com"
                user: User = User.objects.filter(username=username).first()
                if not user:
                    user: User = User.objects.create_user(
                        username=username,
                        **props,
                    )
                    self.stdout.write(
                        f"{username!r} ({user.email}) created with password {props['password']!r}",
                    )
                else:
                    self.stdout.write(f"{username!r} ({user.email}) already exists")
