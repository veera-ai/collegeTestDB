import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table

# Connection string
DB_URI = "mysql+mysqlconnector://admin:pu90c8kV9QoN6j@testdb.c96s4aykk9hv.us-east-1.rds.amazonaws.com:3306/testdb"

# Create engine
engine = create_engine(DB_URI)
metadata = MetaData()

# Define a simple table
sample_table = Table(
    'sample_table', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(50)),
)

try:
    # Create the table
    metadata.create_all(engine)
    print("Table created successfully.")

    # Insert a row and query in the same transaction
    with engine.begin() as conn:
        ins = sample_table.insert().values(name="Test User")
        result = conn.execute(ins)
        print(f"Inserted row with id: {result.inserted_primary_key[0]}")

        # Query the row
        sel = sample_table.select()
        rows = conn.execute(sel).fetchall()
        print("Rows in table:", rows)

except Exception as e:
    print("Error:", e) 