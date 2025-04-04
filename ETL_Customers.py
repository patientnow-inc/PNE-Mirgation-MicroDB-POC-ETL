from sqlalchemy import create_engine
import pandas as pd


# 🏦 SQL Server Connection (Using SQLAlchemy)
SQL_SERVER_CONN_STR = "mssql+pyodbc://onlineadmin:Web2001User@prod-db.envisionnow.com/EnvisionOnlineTest?driver=ODBC+Driver+17+for+SQL+Server"

# 🐘 PostgreSQL Connection
POSTGRES_CONN_STR = "postgresql://user:password123@localhost/PNEMicroDB"

# Define schema mapping (SQL Server → PostgreSQL)
SCHEMA_MAPPING = {
    "customer": {
        "CustomerId": "id",
        "TenantId": "tenant_id",
        "CompanyId": "company_id",
        "CustomerShort": "customer_short",
        "FirstName": "first_name",
        "LastName": "last_name",
        "Email": "email",
        "Birthday": "birthday",         
        "Deleted": "deleted",
        "CreatedOn": "created_on",
    },
    # Add mappings for all tables here...
}

def get_sql_server_engine():
    """Establish connection to SQL Server using SQLAlchemy"""
    return create_engine(SQL_SERVER_CONN_STR)

def get_postgres_engine():
    """Establish connection to PostgreSQL using SQLAlchemy"""
    return create_engine(POSTGRES_CONN_STR)

def extract_data(table_name):
    """Extract data from SQL Server"""
    query = f"SELECT top(100) CustomerId,TenantId,CompanyId,CustomerShort,FirstName,LastName,Email,Birthday,Deleted,CreatedOn FROM  EnvisionOnlineTest.dbo.{table_name}"
    engine  = get_sql_server_engine()
    df = pd.read_sql(query, engine)
    return df

def transform_data(df, table_name):
    """Transform data before inserting into PostgreSQL"""
    if table_name not in SCHEMA_MAPPING:
        return df  # No transformation needed

    # Rename columns
    df = df.rename(columns=SCHEMA_MAPPING[table_name])

    # Convert data types
    for column in df.columns:
        if column in ["deleted", "online_booking_allowed"]:
            df[column] = df[column].astype(bool)  # Convert BIT to BOOLEAN
        elif column in ["birthday"]:
            df[column] = pd.to_datetime(df[column]).dt.date  # Convert DATETIME to DATE
        elif column in ["lastVisit", "created_on"]:
            df[column] = pd.to_datetime(df[column])  # Convert DATETIME to TIMESTAMP

    # Convert NaN values to None for PostgreSQL compatibility
    df = df.where(pd.notnull(df), None)

    return df

def load_data(df, table_name):
    """Load transformed data into PostgreSQL"""
    if df.empty:
        print(f"⚠️ No data to migrate for {table_name}")
        return

    engine = get_postgres_engine()

    # Append data to PostgreSQL
    df.to_sql(table_name, engine, if_exists="append", index=False)
    print(f"✅ Table {table_name} migrated successfully!")

def etl_process():
    """Run ETL Process for all tables"""
    for table in SCHEMA_MAPPING.keys():
        print(f"🔄 Extracting Data from {table}...")
        df = extract_data(table)

        print(f"🔄 Transforming Data for {table}...")
        df_transformed = transform_data(df, table)

        print(f"🔄 Loading Data into PostgreSQL for {table}...")
        load_data(df_transformed, table)

    print("🚀 ETL Process Completed for all tables!")

if __name__ == "__main__":
    etl_process()