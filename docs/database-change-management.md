# Database change management

## Changing Django-managed objects

Django managed objects include tables/views/materialized views,
that are backed by Django models, and their foreign keys/indices/constraints.
It is not recommended to change them directly in database,
because they rely on built-in Django migrations mechanism.

As soon as there's a need to change such object,
there is a pretty straightforward way to do it:

- Change corresponding Django model(s) according to needs;
- Run `makemigrations` command:

  ```commandline
  pipenv run python manage.py makemigrations
  ```

  It will generate migration files with described changes.
  Migration files are located under `{app_name}/migrations` folder,
  and numerated in order they were created.

- Run `migrate` command:

  ```commandline
  pipenv run python manage.py migrate
  ```

  It will apply any un-applied migrations to connected database, as well as new ones.
- Review applied changes at connected database.
  If something is wrong, it is possible to **revert** applied migrations,
  but, as well as with migrations themselves,
  in some cases there might be troubles preserving data on changing tables,
  and some changes could trigger **data loss**.
  So, it is recommended to develop migrations on local database
  with no important data to lose.

  To revert particular migration, execute `migrate` command with additional arguments.

  For example, if in `genphen` app you have migrations,
  numbered **0001**, **0002**, **0003**,
  and you want to revert all changes till **0002** (excluding **0002** itself),
  you can do it with next command:

  ```commandline
  pipenv run python manage.py migrate genphen 0002
  ```

  That command will revert migration **0003**,
  and leave database in state of **0002**.

  However, the more clean way to revert single migration might be
  to drop local database entirely, create new empty database
  and reapply all migrations from scratch.

- After changes were reviewed, commit migration files together with code changes.
  Migrations will be distributed across all active environments through CI/CD pipeline.

More on Django migrations can be found in
[official Django documentation](https://docs.djangoproject.com/en/4.1/topics/migrations/).

## Changing non-managed objects

If you need to change tables, that aren't managed by Django,
e.g. `genphensql` or `biosql` schema tables,
the process is slightly differs from one for managed tables.

Still, Django migrations should be used,
but for non-managed tables there's no migration auto-generation feature,
so the migrations should be written manually in **plain SQL**.

In general, there are 2 approaches to make non-managed migration,
**standard**, when you first write migration and then apply it,
and **backdating**, whe you first apply changes on target database(s),
and then incorporating these changes into initial migration.

### Backdating migration

To make backdating migration is to first apply change directly on every environment,
and then incorporate it in any already applied migration (typically initial).
Quick approach, that doesn't require to create new migration file.
Might be the only possible approach for changes,
that were already applied to a database.

> Make sure, that such changes are made to every database instance.

When it comes to incorporating changes, that were already made to a target database,
it might be hard to remember, what exactly was changed,
compared to state made by migrations.

That's where you would want to compare target database state (that you've changed)
to source database state (that is only have migrations applied and not changed manually).

See [Comparing database states](#comparing-database-states) on how you can do it.

### Standard migration

To make standard migration,
is to [write manual migration](#writing-manual-migrations) first,
and then apply it on every environment (through CI/CD).
Recommended, when there is no need to make **backdating** migration.

## Writing manual migrations

To create an empty migration, run following command:

```commandline
pipenv run python manage.py makemigrations --empty {app_name}
```

where `{app_name}` is application name, where you want new migration to be created.
For genphensql schema it will be `genphen` app, for biosql schema - `biosql` app.

The command will create new empty migration, and show its file path.
Inside you will see similar code:

```python
from django.db import migrations


class Migration(migrations.Migration):

    # after which migrations will be applied that migration.
    # autofilled.
    dependencies = [
        ...
    ]

    operations = [
    ]
```

You need `operations` property.
Write your SQL changes as following:

```python
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ...
    ]

    operations = [
        migrations.RunSQL(
            # migration SQL
            "CREATE TABLE test ....;",
            # optional reverse SQL
            "DROP TABLE test"
        )
    ]
```

If you want to specify an SQL file instead of plain SQL string,
you can write a small function for it.

```python
import os
from django.db import migrations, connection



def run_sql_file(filename):
    """Read sql file from app's `sql` directory."""
    sql_dir = os.path.join(os.path.dirname(__file__), "..", "sql")
    with connection.cursor() as cursor:
        with open(os.path.join(sql_dir, filename)) as file:
            cursor.execute(file.read())


# .sql/0004_create_test_table.sql
run_migration = lambda: run_sql_file('0004_create_test_table.sql')
# .sql/0004_create_test_table_reverse.sql
run_reverse = lambda: run_sql_file('0004_create_test_table_reverse.sql')


class Migration(migrations.Migration):

    dependencies = [
        ...
    ]

    operations = [
        migrations.RunPython(
            run_migration,  # migration function
            run_reverse  # optional reverse function
        )
    ]
```

## Comparing database states

There are a couple of tools,
that can help you detect differences between source and target database states.

### JetBrains IDE's

Recommended way to do it is to use Jetbrains IDE's
[Database difference viewer](
https://www.jetbrains.com/help/idea/differences-viewer-for-database-objects.html
),
that comes with paid versions of many Jetbrains IDE's, including PyCharm and DataGrip.

With it, you can compare tables, schemas and whole databases,
by selecting them in **Database Explorer** tab and pressing `Ctrl+D`.

It will generate SQL commands based on changes selected,
that you can then review and pack into a migration.

However, it requires 2 database connections for comparison.
You can create clean local database with only migrations applied,
and compare it against one that you've changed on dev/uat/other environment.

### Liquibase

Another tool, that can be used, called [Liquibase](https://docs.liquibase.com/home.html),
and it's open-source version is free.

It is complete database change management solution,
and it also allows you to compare database schema against another database
or against local file snapshot.

Maintaining database state snapshot file allows you to have only one database connection.
That way, current database state will be compared against previous recorded state.

You can even put non-managed tables migration process on Liquibase,
but that should be subject to review before implementing.
Django migrations should not be used together with Liquibase changelog sync feature
for same objects in database.
