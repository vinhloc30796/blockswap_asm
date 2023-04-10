import os
import logging
from typing import List, Dict, Iterable

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

from celery_client import app


@app.task()
def get_stakehouse_accnts(url: str, filename: str) -> Dict:
    with open(filename, "r") as f:
        query = f.read()

    # Query The Graph
    transport = AIOHTTPTransport(url=url)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    results = client.execute(document=gql(query))
    logging.info(f"[Stakehouse GQL] Finished! {results=}")
    return results


def get_bls_list(stakehouseAccounts: Dict) -> Iterable[str]:
    stakehouseAccounts: List[Dict] = stakehouseAccounts["stakehouseAccounts"]
    while stakehouseAccounts:
        stakehouseAccount = stakehouseAccounts.pop()
        blsPubKeyDeposits: List = stakehouseAccount.get("blsPubKeyDeposits")
        if len(blsPubKeyDeposits) == 0:
            continue
        elif len(blsPubKeyDeposits) == 1:
            yield blsPubKeyDeposits[0]["blsPubKey"]
        else:
            # warning
            account_id = stakehouseAccount["accountId"]
            n_keys = len(blsPubKeyDeposits)
            logging.warning(f"Account {account_id} has {n_keys} BLS keys")
            # yield each one then continue
            for blsPubKeyDeposit in blsPubKeyDeposits:
                yield blsPubKeyDeposit["blsPubKey"]


def main():
    url = os.getenv(
        "STAKEHOUSE_GRAPHQL_URL",
        "https://api.thegraph.com/subgraphs/name/bswap-eng/stakehouse-protocol",
    )
    filename = os.getenv("STAKEHOUSE_GRAPHQL_FILE", "stakehouseAccounts.gql")
    accounts = get_stakehouse_accnts(url, filename)

    for key in get_bls_list(accounts):
        print(key)


if __name__ == "__main__":
    main()
