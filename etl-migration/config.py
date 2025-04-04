# config.py - Database configuration file

SQL_SERVER_CONN = "mssql+pyodbc://onlineadmin:Web2001User@prod-db.envisionnow.com/EnvisionOnlineTest?driver=ODBC+Driver+17+for+SQL+Server"
POSTGRES_CONN = "postgresql://user:password123@localhost/PNEMicroDB"

# Table name mappings (Old SQL Server Table → New PostgreSQL Table)
TABLE_MAPPINGS = {
    "customer": "customer",
   }
# Column name mappings (Old SQL Server Column → New PostgreSQL Column)
COLUMN_MAPPINGS = {
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
        "UpdatedOn": "updated_on",
    }
}