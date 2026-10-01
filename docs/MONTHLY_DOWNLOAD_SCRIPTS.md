# Binance 月度数据下载脚本使用指南

本目录包含用于下载 Binance 月度数据的脚本。

## 📁 可用脚本列表

| 脚本 | 数据类型 | 支持的市场 | 支持 Intervals | 说明 |
|------|---------|-----------|---------------|------|
| `download-monthly-klines.py` | K线数据 | spot, um, cm | ✅ | 现货和期货的K线/蜡烛图数据 |
| `download-monthly-trades.py` | 逐笔成交 | spot, um, cm | ❌ | 个人交易数据 |
| `download-monthly-aggTrades.py` | 归集成交 | spot, um, cm | ❌ | 归集后的交易数据 |
| `download-monthly-indexPriceKlines.py` | 指数价格K线 | um, cm | ✅ | 期货指数价格K线 |
| `download-monthly-markPriceKlines.py` | 标记价格K线 | um, cm | ✅ | 期货标记价格K线 |
| `download-monthly-premiumIndexKlines.py` | 溢价指数K线 | um | ✅ | 期货溢价指数K线 |
| `download-futures-fundingRate.py` | 资金费率 | um, cm | ❌ | 期货资金费率 |
| `download-daily-bookTicker.py` | 24小时最优挂单 | um, cm | ❌ | **仅日度数据** |

## 🚀 快速开始

### 1. K线数据下载（支持多种周期）

```bash
# 下载现货日线数据（默认1d周期）
python scripts/download-monthly-klines.py -t spot -s BTCUSDT -y 2024

# 下载小时级别数据
python scripts/download-monthly-klines.py -t spot -s BTCUSDT -i 1h -y 2024

# 下载期货数据
python scripts/download-monthly-klines.py -t um -s BTCUSDT -i 1h -y 2024

# 下载多个周期
python scripts/download-monthly-klines.py -t spot -s BTCUSDT -i 1h 4h 1d -y 2024
```

### 2. 成交数据下载

```bash
# 下载逐笔成交
python scripts/download-monthly-trades.py -t spot -s BTCUSDT -y 2024

# 下载归集成交
python scripts/download-monthly-aggTrades.py -t spot -s BTCUSDT -y 2024
```

### 3. 期货专用数据

```bash
# 下载指数价格K线
python scripts/download-monthly-indexPriceKlines.py -t um -s BTCUSDT -i 1h -y 2024

# 下载标记价格K线
python scripts/download-monthly-markPriceKlines.py -t um -s BTCUSDT -i 1h -y 2024

# 下载溢价指数K线
python scripts/download-monthly-premiumIndexKlines.py -s BTCUSDT -i 1h -y 2024

# 下载资金费率
python scripts/download-futures-fundingRate.py -t um -s BTCUSDT -y 2024

# 下载最优挂单（仅日度数据）
python scripts/download-daily-bookTicker.py -t um -s BTCUSDT -y 2024
```

## 📋 通用参数说明

| 参数 | 说明 | 示例 | 默认值 |
|------|------|------|--------|
| `-t` | 市场类型 | `spot`, `um`, `cm` | 因脚本而异 |
| `-s` | 交易对 | `BTCUSDT ETHUSDT` | 自动获取所有 |
| `-i` | K线周期 | `1m 5m 1h 1d` | `1d` |
| `-y` | 年份 | `2023 2024` | 2020-当前年份 |
| `-m` | 月份 | `1 6 12` | 1-12 (全部) |
| `-folder` | 输出目录 | `/data/binance` | 当前目录 |
| `--no-skip-existing` | 强制重新下载 | - | 跳过已存在文件 |
| `-log-level` | 日志级别 | `DEBUG INFO WARNING` | `INFO` |

## 🔄 支持的 K线周期

对于支持 intervals 的数据类型：

- **分钟级**: `1m`, `3m`, `5m`, `15m`, `30m`
- **小时级**: `1h`, `2h`, `4h`, `6h`, `8h`, `12h`
- **日级**: `1d`
- **周级**: `1w`
- **月级**: `1mo`

## 📂 文件保存位置

### 现货数据 (spot)
```
J:\binance-public-data\data\spot\monthly\{数据类型}\{交易对}\{交易对}-{数据类型}-{年份}-{月份}.zip
```

### 期货数据 (um/cm)
```
J:\binance-public-data\data\futures\{市场类型}\monthly\{数据类型}\{交易对}\{交易对}-{数据类型}-{年份}-{月份}.zip
```

### 示例
```
# 现货K线
data\spot\monthly\klines\BTCUSDT\1d\BTCUSDT-1d-2024-01.zip

# 期货K线
data\futures\um\monthly\klines\BTCUSDT\1h\BTCUSDT-1h-2024-01.zip

# 资金费率
data\futures\um\monthly\fundingRate\BTCUSDT\BTCUSDT-fundingRate-2024-01.zip
```

## ⚙️ 特性说明

### ✅ 所有脚本共有的特性

1. **10 线程并发下载** - 显著提升下载速度
2. **自动跳过已存在文件** - 避免重复下载
3. **详细日志输出** - 显示交易对、日期、文件大小
4. **自动获取所有交易对** - 不指定 `-s` 时自动获取
5. **线程安全** - 每次下载使用独立的 SSL 上下文
6. **自动重试** - 网络错误自动重试 3 次

### 📊 数据类型特性对比

| 数据类型 | 月度数据 | 日度数据 | 支持 Intervals | 适用市场 |
|---------|---------|---------|---------------|---------|
| Klines | ✅ | ✅ | ✅ | spot, um, cm |
| Trades | ✅ | ✅ | ❌ | spot, um, cm |
| AggTrades | ✅ | ✅ | ❌ | spot, um, cm |
| IndexPriceKlines | ✅ | ✅ | ✅ | um, cm |
| MarkPriceKlines | ✅ | ✅ | ✅ | um, cm |
| PremiumIndexKlines | ✅ | ✅ | ✅ | um only |
| FundingRate | ✅ | ❌ | ❌ | um, cm |
| BookTicker | ❌ | ✅ | ❌ | um, cm |

## 💡 使用示例

### 示例 1: 下载 BTC 和 ETH 的现货数据

```bash
# 下载 K线（多个周期）
python scripts/download-monthly-klines.py -t spot -s BTCUSDT ETHUSDT -i 1h 1d -y 2024

# 下载成交数据
python scripts/download-monthly-trades.py -t spot -s BTCUSDT ETHUSDT -y 2024

# 下载归集成交
python scripts/download-monthly-aggTrades.py -t spot -s BTCUSDT ETHUSDT -y 2024
```

### 示例 2: 下载期货数据

```bash
# USD-M 期货
python scripts/download-monthly-klines.py -t um -s BTCUSDT -i 1h -y 2024
python scripts/download-monthly-indexPriceKlines.py -t um -s BTCUSDT -i 1h -y 2024
python scripts/download-monthly-markPriceKlines.py -t um -s BTCUSDT -i 1h -y 2024
python scripts/download-futures-fundingRate.py -t um -s BTCUSDT -y 2024

# COIN-M 期货
python scripts/download-monthly-klines.py -t cm -s BTCUSD_PERP -i 1h -y 2024
python scripts/download-monthly-indexPriceKlines.py -t cm -s BTCUSD_PERP -i 1h -y 2024
```

### 示例 3: 下载多年数据

```bash
# 下载 2020-2024 年的所有数据
python scripts/download-monthly-klines.py -t spot -s BTCUSDT -i 1d -y 2020 2021 2022 2023 2024
```

### 示例 4: 下载特定月份

```bash
# 只下载 1 月和 12 月的数据
python scripts/download-monthly-klines.py -t spot -s BTCUSDT -i 1d -y 2024 -m 1 12
```

### 示例 5: 下载所有交易对

```bash
# 不指定 -s，自动下载所有交易对
python scripts/download-monthly-klines.py -t spot -i 1d -y 2024

# 注意：这会下载大量数据，请确保有足够的磁盘空间
```

## 🔍 调试和故障排除

### 查看详细日志

```bash
# 使用 DEBUG 级别查看详细信息
python scripts/download-monthly-klines.py -t spot -s BTCUSDT -y 2024 -log-level DEBUG
```

### 验证下载的文件

```bash
# Windows
dir /s /b data\spot\monthly\klines\BTCUSDT\*.zip

# Linux/Mac
find data/spot/monthly/klines/BTCUSDT/ -name "*.zip"
```

### 强制重新下载

```bash
# 即使文件存在也重新下载
python scripts/download-monthly-klines.py -t spot -s BTCUSDT -y 2024 --no-skip-existing
```

## 📝 注意事项

1. **BookTicker 只有日度数据** - 使用 `download-daily-bookTicker.py`
2. **FundingRate 只有月度数据** - 使用 `download-futures-fundingRate.py`
3. **PremiumIndexKlines 仅支持 um 市场** - 仅 USD-M 期货可用
4. **多线程下载** - 所有脚本使用 10 个并发线程
5. **磁盘空间** - 下载所有数据会占用大量空间
6. **网络稳定** - 确保网络连接稳定，失败会自动重试

## 🚀 性能说明

使用 10 个并发线程时，下载速度大约提升 **6 倍**：

| 场景 | 单线程 | 10 线程 |
|------|--------|---------|
| 下载 12 个月数据 | ~12 秒 | ~2 秒 |
| 下载 3 年数据 | ~36 秒 | ~6 秒 |
| 下载 10 个交易对 | ~120 秒 | ~20 秒 |

## 🔗 相关文档

- [Funding Rate 下载说明](FUNDING_RATE_DOWNLOAD.md)
- [项目 README](../../README.md)
- [迁移指南](../../MIGRATION.md)
