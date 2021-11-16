"""
This example python script shows how to download the Historical Future Order Book level 2 Data via API.

The data download API is part of the Binance API (https://binance-docs.github.io/apidocs/spot/en/#general-api-information).
For how to use it, you may find info there with more examples, especially SIGNED Endpoint security as in https://binance-docs.github.io/apidocs/spot/en/#signed-trade-user_data-and-margin-endpoint-security

For accessing Futures data, the API account also needs to open a Futures account.
Make sure that the API key has been whitelisted to access the data.
"""

# install the following required packages
import requests
import time
import hashlib
import hmac
from urllib.parse import urlencode
from datetime import datetime

S_URL_V1 = "https://api.binance.com/sapi/v1"

# Replace the API Key and secret_key with your API Key and secret_key
api_key = 'your api_key'  #update with your own api_key
secret_key  = 'your secret_key '  #update with your own secret_key


#Function to genarate the signature
def _sign(params={}):
    data = params.copy()
    ts = str(int(1000 * time.time()))
    data.update({"timestamp": ts})
    h = urlencode(data)
    h= h.replace("%40", "@")

    b = bytearray()
    b.extend(secret_key.encode())

    signature = hmac.new(b, msg=h.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    sig = {"signature": signature}

    return data, sig

#Function to genarate the download ID
def post(path, params={}):
    sign = _sign(params)
    query = urlencode(sign[0]) + "&" + urlencode(sign[1])
    url = "%s?%s" % (path, query)
    header = {"X-MBX-APIKEY": api_key}
    Result_PostFunction = requests.post(url, headers=header, \
        timeout=30, verify=True)
    return Result_PostFunction

#Function to genarate the download link
def get(path, params):
    sign = _sign(params)
    query = urlencode(sign[0]) + "&" + urlencode(sign[1])
    url = "%s?%s" % (path, query)
    header = {"X-MBX-APIKEY": api_key}
    Result_GetFunction = requests.get(url, headers=header, \
        timeout=30, verify=True)
    return Result_GetFunction


timestamp = str(int(1000 * time.time())) # current timestamp which serves as an input for the params variable
# Specify the four input parameters below:
params_ToObtainDownloadID = {"symbol": 'ADAUSDT',    #specify the symbol name
      "startTime": 1635561504914, #specify the starttime
      "endTime": 1635561604914,   #specify the endtime
      "dataType": 'T_DEPTH',      #specify the dataType to be downloaded
      "timestamp": timestamp}
# call the "post" function to obtain the download ID for the specified symbol,dataType and time range combination
path = "%s/futuresHistDataId" % S_URL_V1
result_DownloadID = post(path, params_ToObtainDownloadID)
print(result_DownloadID)
print(result_DownloadID.json())
# print the download ID, an example of the output will be like: {'id': 324225}


# Replace the id (324225) with the result from "print(result_DownloadID.json())"
params_ToObtainDownloadLink = {"downloadId": 324225,
           "timestamp": timestamp}
#call the "get" function to obtain the download link for the spicified symbol,dataType and time range combination
Path_ToObtainDownloadLink = "%s/downloadLink" % S_URL_V1
Result_ToBeDownloaded = get(Path_ToObtainDownloadLink, params_ToObtainDownloadLink)
print(Result_ToBeDownloaded)
print(Result_ToBeDownloaded.json())
"""
Output will be a link to download the specific data you requested with the specific parameters.
Sample output will be like the following: {'expirationTime': 1635825806, 'link': 'https://bin-prod-user-rebate-bucket.s3.amazonaws.com/future-data-download/XXX'
Copy the link to the browser and download the data. The link would expire after the expirationTime (usually 24 hours).

Or output will be a message reminding you to re-run the code and download the data hours later.
Sample output will be like the following: {'link': 'Link is preparing; please request later. Notice: when date range is very large (across months), we may need hours to generate.'}
"""