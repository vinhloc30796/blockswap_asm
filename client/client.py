import os
import logging
from typing import List, Dict, Iterable

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport


def get_results() -> Dict:
    url = os.getenv("STAKEHOUSE_GRAPHQL_URL", "https://api.thegraph.com/subgraphs/name/bswap-eng/stakehouse-protocol")
    filename = os.getenv("STAKEHOUSE_GRAPHQL_FILE", "stakehouseAccounts.gql")
    with open(filename, "r") as f:
        query = f.read()

    # Query The Graph
    transport = AIOHTTPTransport(url=url)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    results = client.execute(document=gql(query))
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
            logging.warning(f"Account {stakehouseAccount['accountId']} has {len(blsPubKeyDeposits)} BLS keys")
            # yield each one then continue
            for blsPubKeyDeposit in blsPubKeyDeposits:
                yield blsPubKeyDeposit["blsPubKey"]



if __name__ == "__main__":
    results = get_results()
    # print(results)
    for key in get_bls_list(results):
        print(key)


