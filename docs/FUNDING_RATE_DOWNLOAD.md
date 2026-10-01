# Funding Rate 下载说明

## 概述

本脚本用于下载 Binance 期货的 Funding Rate（资金费率）数据。

**重要**: Funding Rate 数据只有**月度文件**，没有日度文件。

## 多线程配置

脚本当前配置使用 **10 个并发线程**进行下载。

### 多线程实现原理

- 使用 `ThreadPoolExecutor` 实现并发下载
- 每个线程独立处理一个文件的下载
- SSL 上下文为每次下载创建新的实例，确保线程安全
- 自动重试机制处理网络错误

### 线程数配置位置

在 `scripts/download-futures-fundingRate.py` 中：

```python
# 第 83-86 行
downloader = FundingRateDownloader(
    trading_type=trading_type,
    max_workers=10  # 使用 10 个线程
)
```

### 性能说明

| 线程数 | 说明 |
|--------|------|
| 5      | 较保守，适合网络不稳定的情况 |
| 10     | **当前配置**，平衡性能和稳定性 |
| 15+    | 可能被服务器限流，不建议使用 |

## 使用方法

### 基本用法

```bash
# 下载单个交易对
python scripts/download-futures-fundingRate.py -s BTCUSDT -y 2024

# 下载多个交易对
python scripts/download-futures-fundingRate.py -s BTCUSDT ETHUSDT -y 2024

# 下载多年数据
python scripts/download-futures-fundingRate.py -s BTCUSDT -y 2023 2024

# 下载特定月份
python scripts/download-futures-fundingRate.py -s BTCUSDT -y 2024 -m 1 2 3
```

### 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `-t` | 市场类型 (um/cm) | `-t um` |
| `-s` | 交易对符号 | `-s BTCUSDT ETHUSDT` |
| `-y` | 年份 | `-y 2023 2024` |
| `-m` | 月份 (1-12) | `-m 1 6 12` |
| `-folder` | 输出目录 | `-folder /data/binance` |
| `--no-skip-existing` | 强制重新下载 | `--no-skip-existing` |
| `-log-level` | 日志级别 | `-log-level DEBUG` |

### 默认值

- **市场类型**: `um` (USD-M 期货)
- **年份**: 2020 到当前年份
- **月份**: 全部月份 (1-12)
- **线程数**: 10 个并发线程

## 文件保存位置

下载的文件保存在：

```
J:\binance-public-data\data\futures\um\monthly\fundingRate\{SYMBOL}\{SYMBOL}-fundingRate-{YEAR}-{MONTH}.zip
```

例如：
```
J:\binance-public-data\data\futures\um\monthly\fundingRate\BTCUSDT\BTCUSDT-fundingRate-2024-01.zip
```

## 特性

### ✅ 多线程并发下载
- 10 个线程同时下载
- 显著提升下载速度

### ✅ 智能跳过
- 自动检测本地已有文件
- 避免重复下载

### ✅ 详细日志
- 显示交易对和日期
- 显示下载进度和文件大小
- 错误日志清晰明确

### ✅ 线程安全
- 每次下载创建独立的 SSL 上下文
- 避免多线程冲突

### ✅ 自动重试
- 网络错误自动重试
- 最多 3 次重试机会

## 示例输出

```
2026-01-18 15:40:58 - INFO - Using 10 threads for concurrent downloads
2026-01-18 15:40:58 - INFO - Processing symbol: ETHUSDT
2026-01-18 15:40:58 - INFO - Starting monthly download...
2026-01-18 15:40:58 - INFO - [DOWNLOAD] Symbol: ETHUSDT | Date: 2024-01
2026-01-18 15:40:58 - INFO - [OK] Download completed: Symbol: ETHUSDT | Date: 2024-01 | Size: 685.0B
2026-01-18 15:40:58 - INFO - [DOWNLOAD] Symbol: ETHUSDT | Date: 2024-02
2026-01-18 15:40:59 - INFO - [OK] Download completed: Symbol: ETHUSDT | Date: 2024-02 | Size: 770.0B
```

## 故障排除

### 下载速度慢
- 检查网络连接
- 确认 Binance 数据服务器可访问
- 尝试减少线程数（修改 max_workers）

### 部分文件下载失败
- 查看日志中的错误信息
- 重新运行脚本会自动跳过已下载的文件
- 使用 `--no-skip-existing` 强制重新下载

### 线程安全错误
- 当前版本已修复 SSL 上下文的线程安全问题
- 每次下载使用独立的 SSL 上下文

## 性能对比

| 场景 | 单线程 | 10 线程 |
|------|--------|---------|
| 下载 12 个月数据 | ~12 秒 | ~2 秒 |
| 下载 3 年数据 | ~36 秒 | ~6 秒 |
| 下载 10 个交易对 | ~120 秒 | ~20 秒 |

*注：实际性能取决于网络速度和服务器响应时间*
