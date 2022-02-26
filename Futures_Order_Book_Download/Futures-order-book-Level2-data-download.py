"""
This example python script shows how to download the Historical Future Order Book level 2 Data via API.

The data download API is part of the Binance API (https://binance-docs.github.io/apidocs/spot/en/#general-api-information).
For how to use it, you may find info there with more examples, especially SIGNED Endpoint security as in https://binance-docs.github.io/apidocs/spot/en/#signed-trade-user_data-and-margin-endpoint-security

Before executing this file, please note:
    - The API account needs to have a Futures account to access Futures data.
    - The API key has been whitelisted to access the data.
    - Read the comments section in this file to know where you should specify your request values.
"""

# Install the following required packages
import requests
import time
import hashlib
import hmac
from urllib.parse import urlencode

S_URL_V1 = "https://api.binance.com/sapi/v1"

# Specify the api_key and secret_key with your API Key and secret_key
api_key = "your_api_key"
secret_key = "your_secret_key "

# Specify the four input parameters below:
symbol = "ADAUSDT"  # specify the symbol name
startTime = 1635561504914  # specify the starttime
endTime = 1635561604914  # specify the endtime
dataType = "T_DEPTH"  # specify the dataType to be downloaded


# Function to generate the signature
def _sign(params={}):
    data = params.copy()
    ts = str(int(1000 * time.time()))
    data.update({"timestamp": ts})
    h = urlencode(data)
    h = h.replace("%40", "@")

    b = bytearray()
    b.extend(secret_key.encode())

    signature = hmac.new(b, msg=h.encode("utf-8"), digestmod=hashlib.sha256).hexdigest()
    sig = {"signature": signature}

    return data, sig


# Function to generate the download ID
def post(path, params={}):
    sign = _sign(params)
    query = urlencode(sign[0]) + "&" + urlencode(sign[1])
    url = "%s?%s" % (path, query)
    header = {"X-MBX-APIKEY": api_key}
    resultPostFunction = requests.post(url, headers=header, timeout=30, verify=True)
    return resultPostFunction


# Function to generate the download link
def get(path, params):
    sign = _sign(params)
    query = urlencode(sign[0]) + "&" + urlencode(sign[1])
    url = "%s?%s" % (path, query)
    header = {"X-MBX-APIKEY": api_key}
    resultGetFunction = requests.get(url, headers=header, timeout=30, verify=True)
    return resultGetFunction


"""
Beginning of the execution.

The final output will be:
- A link to download the specific data you requested with the specific parameters.
Sample output will be like the following: {'expirationTime': 1635825806, 'link': 'https://bin-prod-user-rebate-bucket.s3.amazonaws.com/future-data-download/XXX'
Copy the link to the browser and download the data. The link would expire after the expirationTime (usually 24 hours).

- A message reminding you to re-run the code and download the data hours later.
Sample output will be like the following: {'link': 'Link is preparing; please request later. Notice: when date range is very large (across months), we may need hours to generate.'}
"""

timestamp = str(
    int(1000 * time.time())
)  # current timestamp which serves as an input for the params variable
paramsToObtainDownloadID = {
    "symbol": symbol,
    "startTime": startTime,
    "endTime": endTime,
    "dataType": dataType,
    "timestamp": timestamp,
}

# Calls the "post" function to obtain the download ID for the specified symbol, dataType and time range combination
path = "%s/futuresHistDataId" % S_URL_V1
resultDownloadID = post(path, paramsToObtainDownloadID)
print(resultDownloadID)
downloadID = resultDownloadID.json()["id"]
print(downloadID)  # prints the download ID, example: {'id': 324225}


# Calls the "get" function to obtain the download link for the specified symbol, dataType and time range combination
paramsToObtainDownloadLink = {"downloadId": downloadID, "timestamp": timestamp}
pathToObtainDownloadLink = "%s/downloadLink" % S_URL_V1
resultToBeDownloaded = get(pathToObtainDownloadLink, paramsToObtainDownloadLink)
print(resultToBeDownloaded)
print(resultToBeDownloaded.json())
