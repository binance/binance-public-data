import os
import wget

from config import DATA_PATH

if __name__ == "__main__":
    symbol = "BNBBUSD"
    temporal = "15m"
    date = "2021-10-15"

    data_folder = "{}_{}".format(symbol, temporal)
    data_folder_path = os.path.join(DATA_PATH, data_folder)
    if not os.path.exists(data_folder_path):
        os.makedirs(data_folder_path)

    file = "{}-{}-{}.zip".format(symbol, temporal, date)
    url = "https://data.binance.vision/data/futures/um/daily/markPriceKlines/{}/{}/{}".format(symbol, temporal, file)
    print(url)
    wget.download(url, data_folder_path)
