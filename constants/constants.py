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


# ### DataBase Configurations
# ### [Render's PostgreSQL DB] 
# HOSTNAME = "dpg-cuhpjsqn91rc73c6bkn0-a"
# DATABASE = "cryptocurrencyprodb_2"
# USERNAME = "cryptocurrencyprodb_2_user"
# PASSWORD = "x2Nbj6K0YousQhsMr89uCAKWjrRdyx0q"
# INTERNAL_DB_URL = "postgresql://cryptocurrencyprodb_2_user:x2Nbj6K0YousQhsMr89uCAKWjrRdyx0q@dpg-cuhpjsqn91rc73c6bkn0-a/cryptocurrencyprodb_2"
# EXTERNAL_DB_URL = "postgresql://cryptocurrencyprodb_2_user:x2Nbj6K0YousQhsMr89uCAKWjrRdyx0q@dpg-cuhpjsqn91rc73c6bkn0-a.oregon-postgres.render.com/cryptocurrencyprodb_2"
# PSQL_CMD = "PGPASSWORD=x2Nbj6K0YousQhsMr89uCAKWjrRdyx0q psql -h dpg-cuhpjsqn91rc73c6bkn0-a.oregon-postgres.render.com -U cryptocurrencyprodb_2_user cryptocurrencyprodb_2"


### [Supabase's PostgreSQL DB]
PSQL_CMD = "psql -h db.ocejkqvmwchksbeujgrk.supabase.co -p 5432 -d postgres -U postgres"
PASSWORD = "J83027::11S"
INTERNAL_DB_URL = "postgresql://postgres.ocejkqvmwchksbeujgrk:J83027::11S@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"
EXTERNAL_DB_URL = "postgresql://postgres.ocejkqvmwchksbeujgrk:J83027::11S@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"


