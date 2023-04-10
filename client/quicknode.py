import os
import logging
import requests
from typing import Dict

from celery_client import app

SAMPLE_BLS_KEY = "0x8021cca323eb594a275752032852777098ef5bc7970db412c9c2c10be3f083d1e02fbe5d0992f24e9aa52a9f7815fe59"

@app.task()
def get_validators(bls_key: str = SAMPLE_BLS_KEY) -> Dict:
    """
    Get validator information from Quicknode API

    Arguments:
        bls_key {str} -- BLS public key

    Returns:
        Dict -- Validator information

    Reference: https://www.quicknode.com/docs/ethereum/eth-v1-beacon-states-%7Bstate_id%7D-validators-%7Bvalidator_id%7D
    """
    url = os.environ["QUICKNODE_URL"]
    path = os.getenv("QUICKNODE_PATH", "/eth/v1/beacon/states/finalized/validators/")
    full_url = f"{url}{path}{bls_key}"
    print(full_url)

    # Params
    payload = {}
    headers = {"accept": "application/json"}

    # Make request with Token Based Auth
    res = requests.get(full_url, headers=headers, data=payload)
    return res.json()


def main():
    res = get_validators()
    print(res)


if __name__ == "__main__":
    main()
