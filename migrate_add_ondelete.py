"""
Migration helper: update existing foreign key constraints to include ON DELETE CASCADE

This script will:
 - inspect the database dialect (postgresql or mysql)
 - find FK constraints on target tables/columns
 - drop and recreate them with ON DELETE CASCADE

Run from the backend folder with your venv activated:
    python migrate_add_ondelete.py

BACKUP your database before running in production.
"""
from app import app, db
from sqlalchemy import text
import sys

TARGETS = [
    # (table, column, referred_table, referred_column)
    ('transaction_item', 'product_id', 'product', 'id'),
    ('transaction_item', 'transaction_id', 'transaction', 'id'),
    ('debt_record', 'transaction_id', 'transaction', 'id'),
]


def run():
    with app.app_context():
        engine = db.engine
        dialect = engine.dialect.name
        print('Detected dialect:', dialect)

        if dialect not in ('postgresql', 'mysql'):
            print('This helper only supports PostgreSQL and MySQL (safe migration).')
            print('For SQLite you must recreate tables or use a custom procedure. Aborting.')
            return

        inspector = db.inspect(engine)

        for table, column, ref_table, ref_column in TARGETS:
            fks = inspector.get_foreign_keys(table)
            matched = [fk for fk in fks if column in fk.get('constrained_columns', [])]
            if not matched:
                print(f'No foreign key found on {table}.{column}; skipping')
                continue

            for fk in matched:
                name = fk.get('name')
                referred_table = fk.get('referred_table')
                referred_columns = fk.get('referred_columns')
                print(f'Found FK {name} on {table} -> {referred_table} {referred_columns}')

                try:
                    if dialect == 'postgresql':
                        # DROP CONSTRAINT then ADD with ON DELETE CASCADE
                        drop_sql = f'ALTER TABLE "{table}" DROP CONSTRAINT IF EXISTS "{name}";'
                        add_sql = f'ALTER TABLE "{table}" ADD CONSTRAINT "{name}" FOREIGN KEY ("{column}") REFERENCES "{ref_table}" ("{ref_column}") ON DELETE CASCADE;'
                        print('Executing:', drop_sql)
                        engine.execute(text(drop_sql))
                        print('Executing:', add_sql)
                        engine.execute(text(add_sql))

                    elif dialect == 'mysql':
                        # MySQL constraint names live in the foreign key name; need to DROP FOREIGN KEY
                        drop_sql = f'ALTER TABLE `{table}` DROP FOREIGN KEY `{name}`;'
                        add_sql = f'ALTER TABLE `{table}` ADD CONSTRAINT `{name}` FOREIGN KEY (`{column}`) REFERENCES `{ref_table}` (`{ref_column}`) ON DELETE CASCADE;'
                        print('Executing:', drop_sql)
                        engine.execute(text(drop_sql))
                        print('Executing:', add_sql)
                        engine.execute(text(add_sql))

                    print(f'Successfully updated FK {name} on {table}.{column} -> ON DELETE CASCADE')
                except Exception as e:
                    print(f'Failed to update FK {name} on {table}.{column}:', e)


if __name__ == '__main__':
    try:
        run()
    except Exception as exc:
        print('Migration script failed:', exc)
        sys.exit(1)
