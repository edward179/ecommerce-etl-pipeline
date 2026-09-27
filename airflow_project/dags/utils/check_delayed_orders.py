import os
import sys
from pathlib import Path

import snowflake.connector

try:
    from dotenv import load_dotenv

    # Project root .env (git-ignored). Real env vars set by Airflow/CI take precedence.
    load_dotenv(Path(__file__).resolve().parents[3] / ".env", override=False)
except ImportError:
    pass

REQUIRED = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_ROLE",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
    "SNOWFLAKE_SCHEMA",
]


def load_snowflake_config():
    missing = [k for k in REQUIRED if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing environment variables: {', '.join(missing)} (see .env.example)")
    return {k.removeprefix("SNOWFLAKE_").lower(): os.environ[k] for k in REQUIRED}


def main():
    print("✅ Running Snowflake delayed orders check...")
    print("✅ Python path:", sys.executable)
    print("✅ Snowflake connector version:", snowflake.connector.__version__)

    try:
        sf_config = load_snowflake_config()
        conn = snowflake.connector.connect(
            user=sf_config["user"],
            password=sf_config["password"],
            account=sf_config["account"],
            warehouse=sf_config["warehouse"],
            database=sf_config["database"],
            schema=sf_config["schema"],
            role=sf_config["role"],
            login_timeout=20,
            client_session_keep_alive=False,
            ocsp_fail_open=True
        )
        print("✅ Connected to Snowflake")

        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*)
            FROM ORDERS_STATUS
            WHERE FINAL_STATUS = 'DELAYED'
        """)
        result = cur.fetchone()
        print("✅ Query Result:", result)
        cur.close()
        conn.close()

        if result[0] > 0:
            raise Exception(f"{result[0]} delayed orders found.")

    except Exception as e:
        print("❌ Error:", e)
        sys.exit(1)  # non-zero exit = task fail

if __name__ == "__main__":
    main()
