import os, sys, re, shutil
import json
from pathlib import Path
from datetime import *
import urllib.request
from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError
from enums import *

def get_destination_dir(file_url, folder=None):
  '''
  获取文件的保存路径
  file_url: 文件在网络上的路径
  folder: 保存文件的目录
  '''
  store_directory = os.environ.get('STORE_DIRECTORY')
  if folder:
    store_directory = folder
  if not store_directory:
    store_directory = os.path.dirname(os.path.realpath(__file__))
  return os.path.join(store_directory, file_url)

def get_download_url(file_url):
  '''
  获取文件的下载路径
  file_url: 文件在网络上的路径
  '''
  return "{}{}".format(BASE_URL, file_url)

def get_all_symbols(type):
  '''
  获取所有交易币种
  type: 交易类型（现货、美元本位合约、币本位合约）
  '''
  if type == 'um':
    response = urllib.request.urlopen("https://fapi.binance.com/fapi/v1/exchangeInfo").read()
  elif type == 'cm':
    response = urllib.request.urlopen("https://dapi.binance.com/dapi/v1/exchangeInfo").read()
  else:
    response = urllib.request.urlopen("https://api.binance.com/api/v3/exchangeInfo").read()
  return list(map(lambda symbol: symbol['symbol'], json.loads(response)['symbols']))

def download_file(base_path, file_name, date_range=None, folder=None):
  '''
  从网络下载文件
  base_path: 文件在网络上的路径
  file_name: 文件名称
  date_range: 日期范围
  folder: 保存文件的目录
  '''

  #获取文件的保存路径 save_path
  download_path = "{}{}".format(base_path, file_name)
  if folder:
    base_path = os.path.join(folder, base_path)
  if date_range and SAVE_RANGE_SEPARATE_FOLDER:
      date_range = date_range.replace(" ","_")
      base_path = os.path.join(base_path, date_range)
  save_path = get_destination_dir(os.path.join(base_path, file_name), folder)
  
  #检查文件是否存在
  if os.path.exists(save_path):
    print("\n文件已存在！ {}".format(save_path))
    return
  
  # 创建目录
  if not os.path.exists(base_path):
    Path(get_destination_dir(base_path)).mkdir(parents=True, exist_ok=True)

  #正式开始下载文件
  try:
    download_url = get_download_url(download_path)
    dl_file = urllib.request.urlopen(download_url)#连接到网络文件
    length = dl_file.getheader('content-length')#获取文件大小（以字节为单位）
    if length:
      length = int(length)
      blocksize = max(4096,length//100)#设置缓冲区大小

    with open(save_path, 'wb') as out_file:#以二进制写入模式打开文件
      dl_progress = 0#下载进度
      print("\n下载文件: {}".format(save_path))
      while True:
        buf = dl_file.read(blocksize)#读取数据到缓冲区
        if not buf:
          break
        dl_progress += len(buf)
        out_file.write(buf)
        #显示下载进度
        done = int(50 * dl_progress / length)
        sys.stdout.write("\r[%s%s]" % ('#' * done, '.' * (50-done)) )    
        sys.stdout.flush()

  except urllib.error.HTTPError:
    print("\n未找到文件: {}".format(download_url))
    pass

def convert_to_date_object(d):
  #将字符串转换为日期对象
  year, month, day = [int(x) for x in d.split('-')]
  date_obj = date(year, month, day)
  return date_obj

def get_start_end_date_objects(date_range):

  start, end = date_range.split()
  start_date = convert_to_date_object(start)
  end_date = convert_to_date_object(end)
  return start_date, end_date

def match_date_regex(arg_value, pat=re.compile(r'\d{4}-\d{2}-\d{2}')):
  #检查日期格式是否正确
  if not pat.match(arg_value):
    raise ArgumentTypeError
  return arg_value

def check_directory(arg_value):
  #检查文件夹是否存在
  if os.path.exists(arg_value):
    while True:
      option = input('文件夹已存在！是否覆盖？是 / 否')
      if option != 'y' and option != 'n':
        print('无效选项！')
        continue
      elif option == 'y':
        shutil.rmtree(arg_value)
        break
      else:
        break
  return arg_value

def raise_arg_error(msg):
  #抛出参数错误异常
  raise ArgumentTypeError(msg)

def get_path(trading_type, market_data_type, time_period, symbol, interval=None):
  '''
  获取网络上文件路径
  trading_type: 交易类型（现货、美元本位合约、币本位合约）
  market_data_type: 市场数据类型（K线、交易、深度等）
  time_period: 保存数据的时间周期（月度、日线）
  symbol: 币种（BTCUSDT、ETHUSDT等）
  interval: K线周期（1m、1d等）
  '''
  trading_type_path = 'data/spot'
  if trading_type != 'spot':
    trading_type_path = f'data/futures/{trading_type}'
  if interval is not None:
    path = f'{trading_type_path}/{time_period}/{market_data_type}/{symbol.upper()}/{interval}/'
  else:
    path = f'{trading_type_path}/{time_period}/{market_data_type}/{symbol.upper()}/'
  return path

def get_parser(parser_type):
  #命令行参数解析器
  parser = ArgumentParser(description=("这是一段用于下载历史 {} 数据的脚本").format(parser_type), formatter_class=RawTextHelpFormatter)
  parser.add_argument(
      '-s', dest='symbols', nargs='+',
      help='单个符号，或由空格分隔的多个符号')
  parser.add_argument(
      '-y', dest='years', default=YEARS, nargs='+', choices=YEARS,
      help='单个年份或多个以空格分隔的年份。\n -y 2019 2021 表示从 2019 年和 2021 年下载 {} 。'.format(parser_type))
  parser.add_argument(
      '-m', dest='months', default=MONTHS,  nargs='+', type=int, choices=MONTHS,
      help='单个月份或多个以空格分隔的月份。\n -m 2 12 表示从 2 月和 12 月下载 {} 。'.format(parser_type))
  parser.add_argument(
      '-d', dest='dates', nargs='+', type=match_date_regex,
      help='需下载的日期，格式为 [YYYY-MM-DD]。\n可输入单个日期或多个以空格分隔的日期。\n若未解析到参数，则从 {}开始下载。'.format(datetime.strptime(PERIOD_START_DATE, '%Y-%m-%d').strftime('%Y年%m月%d日')))
  parser.add_argument(
      '-startDate', dest='startDate', type=match_date_regex,
      help='下载起始日期（格式：年-月-日）')
  parser.add_argument(
      '-endDate', dest='endDate', type=match_date_regex,
      help='下载结束日期（格式：年-月-日）')
  parser.add_argument(
      '-folder', dest='folder', type=check_directory,
      help='存放下载数据的目录')
  parser.add_argument(
      '-skip-monthly', dest='skip_monthly', default=0, type=int, choices=[0, 1],
      help='输入 1 则跳过月度数据下载，默认值为 0')
  parser.add_argument(
      '-skip-daily', dest='skip_daily', default=0, type=int, choices=[0, 1],
      help='输入 1 则跳过日线数据下载，默认值为 0')
  parser.add_argument(
      '-c', dest='checksum', default=0, type=int, choices=[0,1],
      help='输入 1 则下载校验文件，默认值为 0')
  parser.add_argument(
      '-t', dest='type', required=True, choices=TRADING_TYPE,
      help='有效的交易类型: {}'.format(TRADING_TYPE))

  if parser_type == 'klines':
    parser.add_argument(
      '-i', dest='intervals', default=INTERVALS, nargs='+', choices=INTERVALS,
      help='单个 K 线时间间隔或多个以空格分隔的时间间隔。\n -i 1m 1w 表示下载 1 分钟和 1 周时间间隔的 K 线数据。')
  return parser


