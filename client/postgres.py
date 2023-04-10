import os
import logging
from typing import Dict

import psycopg2
from celery_client import app


def make_conn():
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database="postgres",
    )
    return conn


def make_table(conn: psycopg2.extensions.connection) -> bool:
    with conn.cursor() as cur:
        try:
            cur.execute(
                """
                CREATE TABLE validator_balances (
                    validator_index INTEGER PRIMARY KEY,
                    pubkey TEXT NOT NULL,
                    balance BIGINT NOT NULL,
                    withdrawn BOOLEAN NOT NULL
                )
                """
            )
        except psycopg2.errors.DuplicateTable:
            logging.warning("[Validator] Table already exists")
            return False
        except Exception as e:
            logging.error(f"[Validator] {e}")
            return False
        conn.commit()
        return True


def legible_validator(validator: Dict) -> bool:
    data = validator.get("data")
    if not data:
        logging.warning("[Validator] No data")
        return False

    status: str = data.get("status")
    if "withdrawal" in status or "exited" in status:
        return True
    return False


@app.task
def insert_validator_balances(validator: Dict) -> bool:
    # if not legible_validator(validator):
    #     return False
    with make_conn() as conn:
        with conn.cursor() as cur:
            data = validator["data"]
            try:
                cur.execute(
                    """
                    INSERT INTO validator_balances (validator_index, pubkey, balance, withdrawn)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (data["index"], data["validator"]["pubkey"], data["balance"], True),
                )
            except psycopg2.errors.UniqueViolation:
                logging.warning("[Validator] Validator already exists")
                return False
            except Exception as e:
                logging.error(f"[Validator] {e}")
                return False
            conn.commit()
            return True
        

@app.task
def calc_sum_balances() -> int:
    with make_conn() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    SELECT SUM(balance) FROM validator_balances
                    """
                )
                result = cur.fetchone()[0]
                print(f"Total balance: {result}")
                return result
            except Exception as e:
                logging.error(f"[Validator] {e}")
                return False


if __name__ == "__main__":
    with make_conn() as conn:
        make_table_res = make_table(conn)
        logging.info(f"[PostgreSQL] Made table? {make_table_res=}")
