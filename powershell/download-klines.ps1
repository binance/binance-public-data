# This is a simple script to download klines by given parameters.

$symbols = @("BNBUSDT", "BTCUSDT") # add symbols here to download
$intervals = @("1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1mo")
$years = @("2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024")
$months = 1..12 | ForEach-Object { ("{0:D2}" -f $_) }

$baseurl = "https://data.binance.vision/data/spot/monthly/klines"

foreach ($symbol in $symbols) {
    foreach ($interval in $intervals) {
        foreach ($year in $years) {
            foreach ($month in $months) {
                $url = "${baseurl}/${symbol}/${interval}/${symbol}-${interval}-${year}-${month}.zip"
                try {
                    $webRequest = Invoke-WebRequest -Uri $url -Method HEAD -ErrorAction Stop
                    if ($webRequest.StatusCode -eq 200) {
                        Invoke-WebRequest -Uri $url -OutFile "$symbol-$interval-$year-$month.zip"
                        Write-Output "downloaded: $url"
                    } else {
                        Write-Output "File not exist: $url"
                    }
                } catch {
                    Write-Output "File not exist: $url"
                }
            }
        }
    }
}
