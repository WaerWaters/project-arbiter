import tweepy
import requests
from datetime import datetime
import time
from PIL import Image
import io
import urllib.request

last_run = {}
current_run = {}

def job(last_run, current_run):
    collection_ids = []

    url = 'https://api.opencnft.io/2/market/rank/collection'
    headers = {'X-Api-Key': "ocnft_643463f65df520470c76503c"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        for collection in data["ranking"]:
            collection_ids.append(collection["policies"][0])
    else:
        print(f"Error: {response.status_code}")

    check_count = 1
    checked_count = 0
    
    biggest_loss = 0
    asset_name = ""
    wallet = ""
    stake = ""
    time = None
    username = "none"
    social_links = ""
    discord_handle = "none"
    time_str = ""
    image_data = None
    check_tx = False
    
    for collection_id in collection_ids:
        first_tx = True
        
        if last_run:
            if collection_id in last_run:
                check_tx = True
            else:
                check_tx = False
        
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
            for collection_transaction in data["transactions"]:
                if check_tx:
                    if collection_transaction["tx_hash"] == last_run[collection_id]:
                        break
                    else:
                        print("lo")
                
                if first_tx == True:
                    current_run[collection_id] = collection_transaction["tx_hash"]
                    first_tx = False
                
                asset_id = collection_transaction["asset_id"]
                url = "https://server.jpgstoreapis.com/token/{}/tx-history".format(asset_id)
                url_pct = "https://server.jpgstoreapis.com/token/{}".format(asset_id)
                
                params = {
                    "limit": 100,
                    "offset": 0,
                }

                response = requests.get(url, params=params)
                response_pct = requests.get(url_pct)

                if response.status_code == 200:
                    pct = 0
                    if response_pct.status_code == 200:
                        data = response_pct.json()
                        if len(data["collections"]["royalties"]) > 1:
                            pct = float(data["collections"]["royalties"]["pct"])
                        else:
                            pct = 0
                        image_data = data
                    else:
                        print(f"Error: {response_pct.status_code}")
                    checked_count += 1
                    # Parse the JSON response
                    data = response.json()
                    BUY_transactions = []
                    for asset_transaction in data["txs"]:
                        if asset_transaction.get("action") == "BUY" or asset_transaction.get("action") == "ACCEPT_OFFER" or asset_transaction.get("action") == "ACCEPT_COLLECTION_OFFER":
                            BUY_transactions.append(asset_transaction)
                            if len(BUY_transactions) == 2:
                                break
                    if len(BUY_transactions) == 1:
                        print("check({}/{}): bought {} from mint".format(checked_count, check_count*len(collection_ids), collection_transaction["display_name"]))
                    elif len(BUY_transactions) == 2:
                        if int(BUY_transactions[0]["amount_lovelace"]) * (1-pct) < int(BUY_transactions[1]["amount_lovelace"]):
                            loss = int(int(BUY_transactions[1]["amount_lovelace"])/1_000_000 - int(BUY_transactions[0]["amount_lovelace"])/1_000_000 * (1-pct))
                            print("check({}/{}): bought {} from jpg.store and sold for a {}ada loss".format(checked_count, check_count*len(collection_ids), collection_transaction["display_name"], loss))
                            if loss > biggest_loss:
                                biggest_loss = loss
                                asset_name = collection_transaction["display_name"]
                                wallet = BUY_transactions[0]["seller_address"]
                                stake = collection_transaction["seller_stake_key"]
                                time = datetime.fromisoformat(BUY_transactions[0]["confirmed_at"][:-1]) - datetime.fromisoformat(BUY_transactions[1]["confirmed_at"][:-1])
                        else:
                            profit = int(int(BUY_transactions[0]["amount_lovelace"])/1_000_000 * (1-pct) - int(BUY_transactions[1]["amount_lovelace"])/1_000_000)
                            print("check({}/{}): bought {} from jpg.store and sold for a {}ada profit".format(checked_count, check_count*len(collection_ids), collection_transaction["display_name"], profit))
                    else:
                        pass
                else:
                    print(f"Error: {response.status_code}")
        else:
            print(f"Error: {response.status_code}")
    if stake == "":
        print("no jpg.store puchases")
    else:
        url = "https://server.jpgstoreapis.com/user/{}/profile".format(stake)
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            #print(data)
            if data["username"] is not None:
                username = data["username"]
            if data["discord_handle"] is not None:
                discord_handle = data["discord_handle"]
            if data["social_links"] is not None and len(data["social_links"]) != 0:
                for social_link in data["social_links"]:
                    link = data["social_links"].get(social_link)
                    if link is not None:
                        combined = " {}: {},".format(social_link, link)
                        social_links = social_links + combined
            else:
                social_links = " none,"
            
            if time.days == 0 and time.seconds // 3600 == 0:
                time_str = f'{(time.seconds // 60) % 60} minutes'
            elif time.days == 0:
                time_str = f'{time.seconds // 3600} hours, {(time.seconds // 60) % 60} minutes'
            elif time.days != 0 and time.seconds // 3600 == 0:
                time_str = f'{time.days} days'
            elif time.days != 0 and time.seconds // 3600 != 0 and (time.seconds // 60) % 60 == 0:
                time_str = f'{time.days} days, {time.seconds // 3600} hours'
            else:
                time_str = f'{time.days} days, {time.seconds // 3600} hours, {(time.seconds // 60) % 60} minutes'
                
            primary_final_str = "The biggest loser is username: {}, discord handle: {}, wallet: {}, social links:{} who sold {} for a {}ada loss, after holding it for {}".format(username, discord_handle, stake, social_links, asset_name, biggest_loss, time_str)
            print(primary_final_str)


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
            
            # Handle image
            image_content = None
            if "ipfs" in image_data["files"]:
                image_content = requests.get(f'https://ipfs.io/ipfs/{image_data["files"]["ipfs"]}', timeout=10).content
            else:
                image_content = requests.get(image_data["asset_page_urls"][0]).content
            image = Image.open(io.BytesIO(image_content))
            image.save('image.png')
            with open('image.png', 'rb') as f:
                media = api.media_upload(filename='image.png', file=f)
            
            # Post a tweet
            tweet = primary_final_str
            #api.update_status(status=tweet, media_ids=[media.media_id])
            
            last_run.clear()
            last_run = current_run.copy()
            current_run.clear()
            return last_run, current_run
        else:
            print(f"Error: {response.status_code}")

elapsed_time = []
while True:
    try:
        start_time = time.time()
        last_run, current_run = job(last_run, current_run)
        end_time = time.time()
        elapsed_time.append(int(end_time - start_time)/60)
        print(elapsed_time)
        time.sleep(60*2)
    except Exception as e:
        print(f"Error: {str(e)}")
        time.sleep(60*5) # Wait for 5 minutes before trying again

