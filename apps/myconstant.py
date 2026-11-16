import os

from dotenv import load_dotenv

load_dotenv()

# APP_ENV = "production" (server) ya "development" (local machine). Na likha ho to production.
# Koi bhi value environment variable / .env me set ho to wahi chalti hai, defaults sirf tab lagte hain.
APP_ENV = os.getenv("APP_ENV", "production").strip().lower()
IS_DEVELOPMENT = APP_ENV in ("development", "dev", "local")

_ENV_DEFAULTS = {
    "production": {
        "DB_USERNAME": "root",
        "DB_PASS": "Root_123",
        "DB_HOST": "localhost",
        "DB_PORT": "3306",
        "DB_NAME": "Sageone_reckonone_mmc",
        "URL": "mongodb://localhost:27017/MMC",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        # Must match the redirect URI registered in the Reckon developer portal
        "RECKON_REDIRECT_URI": "https://sagetoreckon.mmcconvert.com/callback",
    },
    "development": {
        "DB_USERNAME": "root",
        "DB_PASS": "Technology_100",
        "DB_HOST": "localhost",
        "DB_PORT": "3306",
        "DB_NAME": "Sageone_reckonone_mmc",
        "URL": "mongodb://localhost:27017",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        # Local callback: ye URL Reckon developer portal me register hona chahiye
        "RECKON_REDIRECT_URI": "http://127.0.0.1:5004/callback",
    },
}
_DEFAULTS = _ENV_DEFAULTS["development" if IS_DEVELOPMENT else "production"]


def _setting(name, *aliases):
    """Env var (ya uska alias) set ho to wahi, warna APP_ENV ka default."""
    for key in (name, *aliases):
        value = os.getenv(key)
        if value is not None:
            return value
    return _DEFAULTS[name]


MDB_USERNAME = _setting("DB_USERNAME", "MDB_USERNAME")
MDB_PASSWORD = _setting("DB_PASS", "MDB_PASSWORD")
MDB_HOST = _setting("DB_HOST")
MDB_PORT = _setting("DB_PORT")
MDB_NAME = _setting("DB_NAME")
# URL "mongodb://host:27017" ho ya "mongodb://host:27017/MMC", dono chalenge (code khud "/MMC" jodta hai)
MONGO_URL = _setting("URL").rstrip("/")
if MONGO_URL.endswith("/MMC"):
    MONGO_URL = MONGO_URL[:-len("/MMC")]
REDIS_HOST = _setting("REDIS_HOST")
REDIS_PORT = int(_setting("REDIS_PORT"))
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "MMC")
MYOB_KEY = "client_id,client_secret,company_file_uri,company_file_id,refresh_token,access_token,redirect_uri"
QBO_KEY = "client_id,client_secret,base_url,company_id,minor_version,User_Agent,access_token,refresh_token"
XERO_KEY = "client_id,client_secret,refresh_token,access_token,xero-tenant-id,re_directURI,scopes,state"
MYOBLEDGER_KEY = "client_id,client_secret,company_file_uri,company_file_id,refresh_token,access_token,redirect_uri"
RECKON_KEY = "user_account,client_id,client_secret,id_secret_encoded,redirect_url,Ocp-Apim-Subscription-Key,token,refresh_token,url,book"
SAGEONE_KEY="api_key,company_id,username,password"

EXCEL_KEY = ""
DELETE_KEY =""
EXCEL = "Excel"
MYOB = "Myob"
QBO = "Qbo"
XERO = "Xero"
DELETE ="Delete"
RECKON ="Reckon"
SAGEONE ="Sageone"
MYOBLEDGER = "Myobledger"
JOB_STATUS_SUCCESSFUL = '1'
JOB_STATUS_IN_PROGRESS= '2'
JOB_STATUS_NOT_STARTED = '3'
JOB_STATUS_FAILED = '4'
RECKON_REDIRECT_URI = _setting("RECKON_REDIRECT_URI")
