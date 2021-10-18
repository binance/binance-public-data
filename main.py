import os
import wget
import zipfile
import pandas as pd

from datetime import datetime
from config import DATA_PATH

if __name__ == "__main__":
    symbol = "BNBBUSD"
    temporal = "15m"
    start_date = "2021-07-01"
    end_date = "2021-10-15"

    data_folder = "{}_{}".format(symbol, temporal)
    data_folder_path = os.path.join(DATA_PATH, data_folder)
    if not os.path.exists(data_folder_path):
        os.makedirs(data_folder_path)

    start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
    date_list = pd.date_range(start_date_dt, end_date_dt, freq="1D")
    for date in date_list:
        zip_file = "{}-{}-{}.zip".format(symbol, temporal, date.strftime("%Y-%m-%d"))
        url = "https://data.binance.vision/data/futures/um/daily/markPriceKlines/{}/{}/{}".format(symbol, temporal, zip_file)
        print(url)
        wget.download(url, data_folder_path)

        zip_file_path = os.path.join(data_folder_path, zip_file)
        if os.path.exists(zip_file_path):
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(data_folder_path)
