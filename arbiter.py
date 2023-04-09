import tweepy
import requests

collection_ids = ["fec7dfa59902eb40f65a62812662769962d5662f2a6bc2804b829881"]
check_count = 20
checked_count = 0
for collection_id in collection_ids:
    url = "https://server.jpgstoreapis.com/collection/{}/transactions".format(collection_id)

    # Set query parameters
    params = {
        "page": 1,
        "count": check_count,
        "name": "",
        "traits": "e30="
    }

    # Make the GET request
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        #print(data["transactions"][0])
        biggest_loss = 0
        for collection_transaction in data["transactions"]:
            asset_id = collection_transaction["asset_id"]

            url = "https://server.jpgstoreapis.com/token/{}/tx-history".format(asset_id)

            params = {
                "limit": 100,
                "offset": 0,
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                checked_count += 1

                # Parse the JSON response
                data = response.json()
                #print(data["txs"])
                BUY_transactions = []
                for asset_transaction in data["txs"]:
                    if asset_transaction.get("action") == "BUY" or asset_transaction.get("action") == "ACCEPT_OFFER" or asset_transaction.get("action") == "ACCEPT_COLLECTION_OFFER":
                        BUY_transactions.append(asset_transaction)
                        if len(BUY_transactions) == 2:
                            break
                if len(BUY_transactions) == 1:
                    print("check({}/{}): bought from mint".format(checked_count, check_count*len(collection_ids)))
                else:
                    if int(BUY_transactions[0]["amount_lovelace"]) < int(BUY_transactions[1]["amount_lovelace"]):
                        loss = int(int(BUY_transactions[1]["amount_lovelace"])/1_000_000 - int(BUY_transactions[0]["amount_lovelace"])/1_000_000)
                        print("check({}/{}): bought from jpg.store and sold for a {}ada loss".format(checked_count, check_count*len(collection_ids), loss))
                        if loss > biggest_loss:
                            biggest_loss = loss
                    else:
                        profit = int(int(BUY_transactions[0]["amount_lovelace"])/1_000_000 - int(BUY_transactions[1]["amount_lovelace"])/1_000_000)
                        print("check({}/{}): bought from jpg.store and sold for a {}ada profit".format(checked_count, check_count*len(collection_ids), profit))
            else:
                print(f"Error: {response.status_code}")
        print("The biggest loser is NAME who sold ASSET_NAME for a {}ada loss, after holding it for TIME".format(biggest_loss))
    else:
        print(f"Error: {response.status_code}")













"""
# Replace with your own API keys and access tokens
API_KEY = '6sEnqX34ef0CJXX2rNv87jJ2H'
API_SECRET_KEY = 'Nr3cGkUsWN5M6H9e0Uga0B5WRjQgUtqoAMj0tHDzhyWOQXx3kT'
ACCESS_TOKEN = '1642973632702951429-OwsYinlJsqAgDqKQmt35YT6ilMhpny'
ACCESS_TOKEN_SECRET = 'DRZDVoYfAvpyf0fj8k5OKtbYFGxmCWamBoXGV7XSYKe4o'

# Authenticate to Twitter
auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# Create an API object
api = tweepy.API(auth)

# Post a tweet
tweet = "v1"
api.update_status(status=tweet)
"""