from backend.services.snowflake_service import load_table

df = load_table("stock")

print(df.head())

print(df.columns)

print(df.shape)