from datetime import *

YEARS = ['2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025', '2026']#年份定义
INTERVALS = ["1s", "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1mo"]#周期格式
DAILY_INTERVALS = ["1s", "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]#下载支持的周期
TRADING_TYPE = ["spot", "um", "cm"]#数据类型：现货、美元本位合约、币本位合约
MONTHS = list(range(1,13))#月份定义
PERIOD_START_DATE = '2020-01-01'#默认起始日期
BASE_URL = 'https://data.binance.vision/'#数据网址

START_DATE = date(int(YEARS[0]), MONTHS[0], 1)#默认开始日期
END_DATE = datetime.date(datetime.now())#默认结束日期
SAVE_RANGE_SEPARATE_FOLDER = False#是否将不同日期范围的数据保存到不同的文件夹中