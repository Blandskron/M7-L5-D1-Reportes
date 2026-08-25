from django.db import migrations


def create_procedure(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute("""
            CREATE OR REPLACE PROCEDURE reports_mark_customer_pending_paid(p_customer_id bigint)
            LANGUAGE plpgsql AS $$
            BEGIN
                UPDATE reports_sale SET status = 'PAID'
                WHERE customer_id = p_customer_id AND status = 'PENDING';
            END;
            $$;
        """)


def drop_procedure(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute("DROP PROCEDURE IF EXISTS reports_mark_customer_pending_paid(bigint);")


class Migration(migrations.Migration):
    dependencies = [("reports", "0001_initial")]
    operations = [migrations.RunPython(create_procedure, drop_procedure)]
