# URLS for Source Data:

# ORIGINAL ->  https://api.coingecko.com/api/v3/coins/markets?vs_currency=Inr&order=market_cap_desc&per_page=250&page=1&sparkline=true&price_change_percentage=24h

# MODIFIED ->  https://api.coingecko.com/api/v3/coins/markets?vs_currency=Inr&order=market_cap_desc&per_page=250&page=1&price_change_percentage=24h


COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/markets"
URL_PARAMS = {
    "vs_currency": "Inr",
    "order": "market_cap_desc",
    "per_page": "50",
    "page": "1",
    "price_change_percentage": "24h",
    "sparkline": "true"
}


### DataBase Configurations
### [Render's PostgreSQL DB] 
# HOSTNAME = "dpg-ctsdo4tumphs73flrbr0-a"
# DATABASE = "crypto_currency_db_cb60"
# USERNAME = "crypto_currency_db_cb60_user"
# PASSWORD = "FJ9tobXuAcfpjoe3MpBShtz6zr1esXW9"
# INTERNAL_DB_URL = "postgresql://crypto_currency_db_cb60_user:FJ9tobXuAcfpjoe3MpBShtz6zr1esXW9@dpg-ctsdo4tumphs73flrbr0-a/crypto_currency_db_cb60"
# EXTERNAL_DB_URL = "postgresql://crypto_currency_db_cb60_user:FJ9tobXuAcfpjoe3MpBShtz6zr1esXW9@dpg-ctsdo4tumphs73flrbr0-a.oregon-postgres.render.com/crypto_currency_db_cb60"
# PSQL_CMD = "PGPASSWORD=FJ9tobXuAcfpjoe3MpBShtz6zr1esXW9 psql -h dpg-ctsdo4tumphs73flrbr0-a.oregon-postgres.render.com -U crypto_currency_db_cb60_user crypto_currency_db_cb60"


### [Supabase's PostgreSQL DB]
PSQL_CMD = "psql -h db.ocejkqvmwchksbeujgrk.supabase.co -p 5432 -d postgres -U postgres"
PASSWORD = "J83027::11S"
INTERNAL_DB_URL = f"postgresql://postgres:{PASSWORD}@db.ocejkqvmwchksbeujgrk.supabase.co:5432/postgres"
EXTERNAL_DB_URL = f"postgresql://postgres:{PASSWORD}@db.ocejkqvmwchksbeujgrk.supabase.co:5432/postgres"


