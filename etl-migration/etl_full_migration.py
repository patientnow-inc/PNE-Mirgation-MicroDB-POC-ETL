import pandas as pd
from sqlalchemy import create_engine
from config import SQL_SERVER_CONN, POSTGRES_CONN, TABLE_MAPPINGS, COLUMN_MAPPINGS


# Create database engines
sql_engine = create_engine(SQL_SERVER_CONN)
pg_engine = create_engine(POSTGRES_CONN)

def get_column_selection(table_name):
    """Generates SQL SELECT query with only mapped columns."""
    column_mapping = COLUMN_MAPPINGS.get(table_name, {})
    sql_columns = ", ".join(column_mapping.keys())  # Get only old table columns
    return sql_columns

def rename_columns(df, table_name):
    """Renames columns based on the mapping defined in config.py."""
    column_mapping = COLUMN_MAPPINGS.get(table_name, {})
    return df.rename(columns=column_mapping)

def migrate_full_data():
    """Extracts all mapped columns from SQL Server, transforms, and loads into PostgreSQL."""
    for old_table, new_table in TABLE_MAPPINGS.items():
        sql_columns = get_column_selection(old_table)
        query = f"SELECT top(100) {sql_columns} FROM dbo.{old_table}"

        print(f"📤 Extracting data from {old_table} with mapped columns...")
        df = pd.read_sql(query, sql_engine)

        # Rename columns
        df = rename_columns(df, old_table)

        print(f"📥 Loading {new_table} into PostgreSQL...")
        df.to_sql(new_table, pg_engine, if_exists="append", index=False)

        print(f"✅ Migration completed for {old_table} -> {new_table}!")

if __name__ == "__main__":
    migrate_full_data()
    print("🎉 Full migration completed successfully!")