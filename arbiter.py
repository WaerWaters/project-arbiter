import tweepy

# Client ID
#NXh1cXhzaS1qeXRhRm92bGJuSzQ6MTpjaQ

#Client Secret
#qWfJUZF_OzWQjvy7HPjkxqecTCnhRqYnb6HAtsVNI7SyiReu13

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