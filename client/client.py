import os
from typing import Dict

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


if __name__ == "__main__":
    results = get_results()
    print(results)


