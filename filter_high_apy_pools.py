#!/usr/bin/env python3
"""
Script to filter Curve pools with gaugeCrvApy values higher than 10.
"""

import json
import os
from typing import Dict, Any, List

def filter_high_apy_pools(file_path: str, all_pools_file_path: str, min_apy: float = 10.0, min_usd_total: float = 1000000.0) -> List[Dict[str, Any]]:
    """
    Filter Curve pools with gaugeCrvApy values higher than the specified minimum and USD total above threshold.
    
    Args:
        file_path: Path to the curvefi-all-guages.json file
        all_pools_file_path: Path to the all-pools.json file
        min_apy: Minimum APY threshold (default: 10.0)
        min_usd_total: Minimum USD total value (default: 1,000,000)
    
    Returns:
        List of pools with high APY values and sufficient TVL
    """
    try:
        # Load gauges data
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if not data.get('success') or 'data' not in data:
            print("Error: Invalid gauges data structure")
            return []
        
        # Load all pools data
        with open(all_pools_file_path, 'r') as f:
            all_pools_data = json.load(f)
        
        if not all_pools_data.get('success') or 'data' not in all_pools_data:
            print("Error: Invalid all-pools data structure")
            return []
        
        # Create a lookup dictionary for pool addresses to USD totals and extra rewards
        pool_usd_lookup = {}
        pool_extra_rewards_lookup = {}
        
        for pool in all_pools_data['data']['poolData']:
            address = pool.get('address', '').lower()
            usd_total = pool.get('usdTotal', 0)
            pool_usd_lookup[address] = usd_total
            
            # Calculate extra rewards APY
            extra_apy = 0.0
            gauge_rewards = pool.get('gaugeRewards', [])
            if gauge_rewards:
                for reward in gauge_rewards:
                    extra_apy += reward.get('apy', 0.0)
            pool_extra_rewards_lookup[address] = extra_apy
        
        pools_data = data['data']
        high_apy_pools = []
        all_pools_with_apy = []
        
        for pool_name, pool_info in pools_data.items():
            # Check if this is a pool and has gaugeCrvApy data
            if not pool_info.get('isPool', False):
                continue
                
            gauge_crv_apy = pool_info.get('gaugeCrvApy')
            if not gauge_crv_apy or not isinstance(gauge_crv_apy, list) or len(gauge_crv_apy) != 2:
                continue
            
            # Skip pools with hasNoCrv = true
            if pool_info.get('hasNoCrv', False):
                continue
            
            # Only include stable pools (USD pools)
            if pool_info.get('type') != 'stable':
                continue
            
            # Exclude pools with BTC or ETH in their name
            pool_name_lower = pool_name.lower()
            if 'btc' in pool_name_lower or 'eth' in pool_name_lower:
                continue
            
            # Get pool address for lookups
            pool_address = pool_info.get('swap', '').lower()
            
            # Check USD total value
            usd_total = pool_usd_lookup.get(pool_address, 0)
            if usd_total < min_usd_total:
                continue
            
            # Get extra rewards APY
            extra_apy = pool_extra_rewards_lookup.get(pool_address, 0.0)
            
            # Check if either APY value (CRV + Extra) is higher than the threshold
            # Handle None values properly
            base_apy_0 = gauge_crv_apy[0] if gauge_crv_apy[0] is not None else 0
            base_apy_1 = gauge_crv_apy[1] if gauge_crv_apy[1] is not None else 0
            
            total_apy_0 = base_apy_0 + extra_apy
            total_apy_1 = base_apy_1 + extra_apy
            
            if total_apy_0 > min_apy or total_apy_1 > min_apy:
                pool_entry = {
                    'name': pool_name,
                    'pool_info': pool_info,
                    'gaugeCrvApy': gauge_crv_apy,
                    'extra_rewards_apy': extra_apy,
                    'total_apy_range': [total_apy_0, total_apy_1],
                    'max_apy': max(total_apy_0, total_apy_1),
                    'usd_total': usd_total
                }
                high_apy_pools.append(pool_entry)
            
            # Also collect all pools with non-zero APY for analysis
            if total_apy_0 > 0 or total_apy_1 > 0:
                all_pools_with_apy.append({
                    'name': pool_name,
                    'gaugeCrvApy': gauge_crv_apy,
                    'extra_rewards_apy': extra_apy,
                    'hasNoCrv': pool_info.get('hasNoCrv', False)
                })
        
        # Sort by maximum APY in descending order
        high_apy_pools.sort(key=lambda x: x['max_apy'], reverse=True)
        
        # Print summary of all pools with non-zero APY
        if all_pools_with_apy:
            print(f"Found {len(all_pools_with_apy)} pools with non-zero APY (CRV + Extra):")
            for pool in all_pools_with_apy[:10]:  # Show first 10
                gauge_apy = pool['gaugeCrvApy']
                extra = pool['extra_rewards_apy']
                print(f"  {pool['name']}: CRV[{gauge_apy[0]:.2f}%, {gauge_apy[1]:.2f}%] + Extra[{extra:.2f}%]")
            if len(all_pools_with_apy) > 10:
                print(f"  ... and {len(all_pools_with_apy) - 10} more")
        else:
            print("No pools found with non-zero APY values")
        
        return high_apy_pools
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def print_results(high_apy_pools: List[Dict[str, Any]], min_apy: float = 10.0):
    """Print the results in a formatted way."""
    if not high_apy_pools:
        print(f"No pools found with Total APY > {min_apy}%")
        return
    
    print(f"Found {len(high_apy_pools)} pools with Total APY > {min_apy}%:")
    print("=" * 80)
    
    for i, pool in enumerate(high_apy_pools, 1):
        pool_info = pool['pool_info']
        gauge_apy = pool['gaugeCrvApy']
        extra_apy = pool['extra_rewards_apy']
        total_apy = pool['total_apy_range']
        
        print(f"{i}. {pool['name']}")
        print(f"   Base CRV APY:   [{gauge_apy[0]:.2f}%, {gauge_apy[1]:.2f}%]")
        print(f"   Extra APY:      {extra_apy:.2f}%")
        print(f"   Total APY:      [{total_apy[0]:.2f}%, {total_apy[1]:.2f}%]")
        print(f"   Max Total APY:  {pool['max_apy']:.2f}%")
        print(f"   USD Total:      ${pool.get('usd_total', 0):,.2f}")
        print(f"   Type:           {pool_info.get('type', 'unknown')}")
        print(f"   Blockchain:     {pool_info.get('blockchainId', 'unknown')}")
        
        # Show pool URLs if available
        pool_urls = pool_info.get('poolUrls', {})
        if pool_urls:
            swap_urls = pool_urls.get('swap', [])
            if swap_urls:
                print(f"   Swap URL:       {swap_urls[0]}")
        
        print("-" * 80)

def main():
    """Main function to run the script."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    file_path = os.path.join(script_dir, "curvefi-all-guages.json")
    all_pools_file_path = os.path.join(script_dir, "all-pools.json")
    min_apy = 7.0
    min_usd_total = 5000000.0  # $5M
    
    print(f"Filtering Curve stable pools (USD pools) with Total APY > {min_apy}% and USD total > ${min_usd_total:,.0f}...")
    high_apy_pools = filter_high_apy_pools(file_path, all_pools_file_path, min_apy, min_usd_total)
    print_results(high_apy_pools, min_apy)
    
    # Optionally save results to a JSON file
    if high_apy_pools:
        output_file = os.path.join(script_dir, "high_apy_stable_pools_1m_plus.json")
        try:
            with open(output_file, 'w') as f:
                json.dump(high_apy_pools, f, indent=2)
            print(f"\nResults saved to: {output_file}")
        except Exception as e:
            print(f"Error saving results: {e}")

if __name__ == "__main__":
    main()
