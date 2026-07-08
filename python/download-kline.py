#!/usr/bin/env python
'''
用于下载 K 线数据的脚本。
请为存储目录（STORE_DIRECTORY）设置目标文件夹的绝对路径，随后执行脚本。
示例：STORE_DIRECTORY=/data/ ./download-kline.py
'''

import sys
from datetime import *
import pandas as pd
from enums import *
from utility import download_file, get_all_symbols, get_parser, get_start_end_date_objects, convert_to_date_object, \
  get_path


def download_monthly_klines(trading_type, symbols, num_symbols, intervals, years, months, start_date, end_date, folder, checksum):
  '''
  下载月 K 线
  trading_type: 交易类型（现货、美元本位合约、币本位合约）
  symbols: 币种列表
  num_symbols: 币种数量
  intervals: K 周期
  years: 支持的年份列表
  months: 月份列表
  start_date: 起始日期
  end_date: 结束日期
  folder: 存放下载数据的目录
  checksum: 是否下载校验文件
  '''
  #当前数量
  current = 0
  date_range = None

  if start_date and end_date:
    date_range = start_date + " " + end_date

  if not start_date:
    start_date = START_DATE
  else:
    start_date = convert_to_date_object(start_date)
    start_date = start_date.replace(day=1)

  if not end_date:
    end_date = END_DATE
  else:
    end_date = convert_to_date_object(end_date)
    end_date = end_date.replace(day=1)

  print("币种列表数量：{}".format(num_symbols))

  for symbol in symbols:
    print("[{}/{}] - 开始下载月度 [{}] K线数据".format(current+1, num_symbols, symbol))
    for interval in intervals:
      for year in years:
        for month in months:
          current_date = convert_to_date_object('{}-{}-01'.format(year, month))

          #判断当前日期是否在起始日期和结束日期之间
          if current_date >= start_date and current_date <= end_date:
            path = get_path(trading_type, "klines", "monthly", symbol, interval)
            file_name = "{}-{}-{}-{}.zip".format(symbol.upper(), interval, year, '{:02d}'.format(month))#获取网络上的文件名称
            download_file(path, file_name, date_range, folder)

            if checksum == 1:
              checksum_path = get_path(trading_type, "klines", "monthly", symbol, interval)
              checksum_file_name = "{}-{}-{}-{}.zip.CHECKSUM".format(symbol.upper(), interval, year, '{:02d}'.format(month))
              download_file(checksum_path, checksum_file_name, date_range, folder)

    current += 1

def download_daily_klines(trading_type, symbols, num_symbols, intervals, dates, start_date, end_date, folder, checksum):
  '''
  下载日 K 线
  trading_type: 交易类型（现货、美元本位合约、币本位合约）
  symbols: 币种列表
  num_symbols: 币种数量
  intervals: K 线时间间隔列表
  dates: 日期列表
  start_date: 起始日期
  end_date: 结束日期
  folder: 存放下载数据的目录
  checksum: 是否下载校验文件
  '''
  current = 0
  date_range = None

  if start_date and end_date:
    date_range = start_date + " " + end_date

  if not start_date:
    start_date = START_DATE
  else:
    start_date = convert_to_date_object(start_date)

  if not end_date:
    end_date = END_DATE
  else:
    end_date = convert_to_date_object(end_date)

  #Get valid intervals for daily
  intervals = list(set(intervals) & set(DAILY_INTERVALS))
  print("Found {} symbols".format(num_symbols))

  for symbol in symbols:
    print("[{}/{}] - start download daily {} klines ".format(current+1, num_symbols, symbol))
    for interval in intervals:
      for date in dates:
        current_date = convert_to_date_object(date)
        if current_date >= start_date and current_date <= end_date:
          path = get_path(trading_type, "klines", "daily", symbol, interval)
          file_name = "{}-{}-{}.zip".format(symbol.upper(), interval, date)
          download_file(path, file_name, date_range, folder)

          if checksum == 1:
            checksum_path = get_path(trading_type, "klines", "daily", symbol, interval)
            checksum_file_name = "{}-{}-{}.zip.CHECKSUM".format(symbol.upper(), interval, date)
            download_file(checksum_path, checksum_file_name, date_range, folder)

    current += 1

if __name__ == "__main__":
    print(sys.argv)
    parser = get_parser('klines')
    args = parser.parse_args(sys.argv[1:])

    #获取币种列表和数量
    if not args.symbols:
      #获取交易所所有币种
      print("从交易所获取全部交易标的")
      symbols = get_all_symbols(args.type)
      num_symbols = len(symbols)
    else:
      #获取币种列表
      symbols = args.symbols
      #获取币种数量
      num_symbols = len(symbols)

    #获取日期列表
    if args.dates:
      dates = args.dates
    else:
      #设置默认起始日期和结束日期
      period = convert_to_date_object(datetime.today().strftime('%Y-%m-%d')) -\
      convert_to_date_object(args.startDate if args.startDate is not None else PERIOD_START_DATE) 
      dates = pd.date_range(end=datetime.today(), periods=period.days + 1).to_pydatetime().tolist()
      dates = [date.strftime("%Y-%m-%d") for date in dates]
    
    #是否下载月度 K 线数据
    if args.skip_monthly == 0:
      download_monthly_klines(args.type, symbols, num_symbols, args.intervals, args.years, args.months, args.startDate, args.endDate, args.folder, args.checksum)
    #是否下载日 K 线数据
    if args.skip_daily == 0:
      download_daily_klines(args.type, symbols, num_symbols, args.intervals, dates, args.startDate, args.endDate, args.folder, args.checksum)

