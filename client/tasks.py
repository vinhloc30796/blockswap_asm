import os
import logging
from typing import List, Dict
from celery import group

from celery_client import app
from thegraph import get_stakehouse_accnts, get_bls_list
from quicknode import get_validators
from postgres import insert_validator_balances, calc_sum_balances

# Set logging level to INFO
logging.basicConfig(level=logging.INFO)


BEAT_SECONDS = 30.0


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls process_all_stakehouse_validators every 30 seconds.
    sender.add_periodic_task(
        BEAT_SECONDS,
        process_all_stakehouse_validators.s(),
        name="process all stakehouse validators",
    )
    sender.add_periodic_task(
        BEAT_SECONDS * 3,
        calc_sum_balances.s(),
        name="calculate sum of balances",
    )


@app.task()
def process_all_stakehouse_validators() -> List[Dict]:
    url = os.getenv(
        "STAKEHOUSE_GRAPHQL_URL",
        "https://api.thegraph.com/subgraphs/name/bswap-eng/stakehouse-protocol",
    )
    filename = os.getenv("STAKEHOUSE_GRAPHQL_FILE", "stakehouseAccounts.gql")

    # Chain Celery tasks: get_stakehouse_accnts, get_bls_list, get_validators
    # 1. Get stakehouse accounts from The Graph
    accounts = get_stakehouse_accnts(url, filename)
    logging.debug(f"Length ({len(accounts)}) {accounts=}")

    # 2. Get BLS keys
    bls_keys = get_bls_list(accounts)

    # 3. Get validator information from BLS keys
    # 4. Insert validator information into Postgres
    vals = group(
        get_validators.s(key) | insert_validator_balances.s()
        for key in bls_keys
        # get_validators.s(key)  for key in bls_keys
    ).apply_async()

    return vals


if __name__ == "__main__":
    # process_all_stakehouse_validators()
    app.start(["-A", "tasks", "worker", "-B", "-E", "--loglevel=warning"])
