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

def migrate_incremental_data():
    """Extracts only updated records from SQL Server and syncs to PostgreSQL."""
    for old_table, new_table in TABLE_MAPPINGS.items():
        sql_columns = get_column_selection(old_table)

        query = f"""
        SELECT top(100) {sql_columns} FROM dbo.{old_table} 
        WHERE UpdatedOn >= (SELECT top(100) COALESCE(MAX(UpdatedOn), '2000-01-01') FROM dbo.{new_table})
        """

        print(f"🔍 Checking for updates in {old_table}...")

        df = pd.read_sql(query, sql_engine)

        if df.empty:
            print(f"✅ No updates for {old_table}.")
            continue

        # Rename columns
        df = rename_columns(df, old_table)

        print(f"📥 Syncing {new_table} with {len(df)} updated records...")
        df.to_sql(new_table, pg_engine, if_exists="append", index=False)

        print(f"✅ Incremental update completed for {old_table} -> {new_table}!")

if __name__ == "__main__":
    migrate_incremental_data()
    print("🎉 Incremental update completed successfully!")