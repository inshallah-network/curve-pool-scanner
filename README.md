# Curve Pool Scanner

A Python script to filter and analyze Curve Finance pools with high APY values.

## Description

This tool scans Curve Finance pools and filters for stable pools (USD pools) that meet specific criteria:
- Minimum APY threshold (default: 7%)
- Minimum USD total value (default: $1M)
- Includes both CRV rewards and extra rewards in APY calculations

## Features

- Filters Curve pools by APY and TVL
- Focuses on stable pools (USD pools)
- Calculates total APY including CRV rewards and extra rewards
- Exports results to JSON format
- Provides detailed pool information including swap URLs

## Requirements

- Python 3.x
- JSON data files:
  - `curvefi-all-guages.json` - Curve gauges data
  - `all-pools.json` - All pools data

## Usage

1. Ensure you have the required JSON data files in the project directory
2. Update the file paths in `filter_high_apy_pools.py` if needed
3. Run the script:

```bash
python3 filter_high_apy_pools.py
```

## Configuration

You can modify the following parameters in the `main()` function:

- `min_apy`: Minimum APY threshold (default: 7.0)
- `min_usd_total`: Minimum USD total value (default: 1,000,000.0)

## Output

The script will:
- Print filtered pools to the console
- Save results to `high_apy_stable_pools_1m_plus.json`

## License

MIT

