# MMC Data Transfer

## Application to transfer data from various tools


## Local setup (Windows)

Requirements: Python 3.12, MySQL 8, MongoDB, Redis, wkhtmltopdf (for PDF reports).

```powershell
py -3.12 -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env      # then edit DB_PASS etc.
```

Create the MySQL database once:

```sql
CREATE DATABASE IF NOT EXISTS Sageone_reckonone_mmc CHARACTER SET utf8mb4;
```

Start MySQL, MongoDB and Redis, then run:

```powershell
.\venv\Scripts\python.exe run.py
```

App: http://127.0.0.1:5004/login (tables are created on first request).
