#!/usr/bin/env python3
"""
IMPROVED: Check Total Token Balance for Wallet Addresses
Uses tokentx endpoint to get accurate token holdings

This fixes the issue where addresstokenbalance misses tokens
"""

import requests
import time
from pathlib import Path
import json
import pandas as pd
from datetime import datetime
from collections import defaultdict


class ImprovedBalanceChecker:
    """Check total wallet balances by analyzing transaction history"""
    
    BASE_URL = "https://api.etherscan.io/v2/api"
    RATE_LIMIT_DELAY = 0.21
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.last_call_time = 0
        
    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - elapsed)
        self.last_call_time = time.time()
    
    def get_eth_balance(self, address: str) -> float:
        """Get ETH balance for an address"""
        self._rate_limit()
        
        params = {
            'chainid': '1',
            'module': 'account',
            'action': 'balance',
            'address': address,
            'tag': 'latest',
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            data = response.json()
            
            if data.get('status') == '1':
                balance_wei = int(data['result'])
                return balance_wei / 1e18
            else:
                return 0.0
        except Exception as e:
            print(f"  Error getting ETH: {e}")
            return 0.0
    
    def get_token_transfers(self, address: str, start_block: int = 0) -> list:
        """Get all ERC-20 token transfers for an address"""
        self._rate_limit()
        
        params = {
            'chainid': '1',
            'module': 'account',
            'action': 'tokentx',
            'address': address,
            'startblock': start_block,
            'endblock': 99999999,
            'sort': 'asc',
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            data = response.json()
            
            if data.get('status') == '1':
                return data.get('result', [])
            else:
                return []
        except Exception as e:
            print(f"  Error getting token transfers: {e}")
            return []
    
    def calculate_token_balances(self, address: str, transfers: list) -> dict:
        """Calculate token balances from transfer history"""
        
        address_lower = address.lower()
        balances = defaultdict(lambda: {
            'balance': 0,
            'decimals': 18,
            'symbol': '',
            'name': '',
            'contract': ''
        })
        
        for tx in transfers:
            token_address = tx.get('contractAddress', '').lower()
            from_addr = tx.get('from', '').lower()
            to_addr = tx.get('to', '').lower()
            value = int(tx.get('value', 0))
            decimals = int(tx.get('tokenDecimal', 18))
            symbol = tx.get('tokenSymbol', 'UNKNOWN')
            name = tx.get('tokenName', '')
            
            # Update token info
            balances[token_address]['decimals'] = decimals
            balances[token_address]['symbol'] = symbol
            balances[token_address]['name'] = name
            balances[token_address]['contract'] = token_address
            
            # Update balance
            if to_addr == address_lower:
                # Received
                balances[token_address]['balance'] += value
            elif from_addr == address_lower:
                # Sent
                balances[token_address]['balance'] -= value
        
        # Convert to decimal and filter non-zero
        result = {}
        for token_addr, info in balances.items():
            decimal_balance = info['balance'] / (10 ** info['decimals'])
            if decimal_balance > 0:  # Only include positive balances
                result[token_addr] = {
                    'symbol': info['symbol'],
                    'name': info['name'],
                    'balance': decimal_balance,
                    'balance_raw': info['balance'],
                    'decimals': info['decimals'],
                    'contract': info['contract']
                }
        
        return result
    
    def check_address(self, address: str, name: str = None) -> dict:
        """Check all balances for an address"""
        
        display_name = name or address[:10] + "..."
        print(f"\nChecking: {display_name}")
        print(f"Address: {address}")
        
        # Get ETH balance
        eth_balance = self.get_eth_balance(address)
        print(f"  ETH: {eth_balance:.6f}")
        
        # Get all token transfers
        print(f"  Fetching token transaction history...")
        transfers = self.get_token_transfers(address)
        print(f"  Found {len(transfers)} token transactions")
        
        # Calculate balances
        print(f"  Calculating current balances...")
        token_balances = self.calculate_token_balances(address, transfers)
        
        result = {
            'address': address,
            'name': name,
            'eth_balance': eth_balance,
            'tokens': []
        }
        
        if token_balances:
            print(f"  Tokens with balance: {len(token_balances)}")
            
            # Sort by balance (descending)
            sorted_tokens = sorted(
                token_balances.items(), 
                key=lambda x: x[1]['balance'], 
                reverse=True
            )
            
            # Show top tokens
            for i, (contract, token_info) in enumerate(sorted_tokens[:20]):
                symbol = token_info['symbol']
                balance = token_info['balance']
                print(f"    {symbol}: {balance:,.4f}")
                
                result['tokens'].append(token_info)
            
            if len(sorted_tokens) > 20:
                print(f"    ... and {len(sorted_tokens) - 20} more tokens")
                # Add remaining tokens to result
                for contract, token_info in sorted_tokens[20:]:
                    result['tokens'].append(token_info)
        else:
            print(f"  No tokens with positive balance")
        
        return result


def main():
    """Main execution"""
    
    print("="*80)
    print("IMPROVED TOTAL WALLET BALANCE CHECKER")
    print("="*80)
    print()
    print("This version analyzes transaction history to calculate accurate")
    print("token balances, including all ERC-20 tokens.")
    print()
    
    # Get API key
    api_key = input("Enter Etherscan API Key: ").strip()
    if not api_key:
        print("Error: API key required")
        return
    
    # Ask which addresses to check
    print()
    print("Which addresses do you want to check?")
    print("1. Primary 6 wallets only (recommended)")
    print("2. Primary 6 + Top 20 Level 1 recipients (26 total)")
    print("3. Custom address list")
    print()
    
    choice = input("Choice (1-3): ").strip()
    
    # Define primary wallets
    primary_wallets = [
        ('0xddbae474cd6e7da39555d71a61e9794822c57968', 'Goliath Wallet 1'),
        ('0xc37a3bb2f061c002f8127ba1e25402193dce862f', 'Goliath Wallet 2'),
        ('0x77696bb39917c91a0c3908d577d5e322095425ca', 'Goliath Wallet 3'),
        ('0x808b4da0be6c9512e948521452227efc619bea52', 'Goliath Wallet 4'),
        ('0xd24400ae8bfebb18ca49be86258a3c749cf46853', 'Goliath Wallet 5'),
        ('0x80787af194c33b74a811f5e5c549316269d7ee1a', '$329M Collection Wallet'),
    ]
    
    # Define top 20 Level 1
    level1_top20 = [
        ('0x134bcda65f481dc2df1c2643dda79740ba5a56e4', 'Level 1 Rank 1: $2.0M'),
        ('0xdece5569d3cf17168ae9f5cfb387fb7cd3299ca7', 'Level 1 Rank 2: $1.95M'),
        ('0xb134034e4e10dd97cd2149395f517240e88c1276', 'Level 1 Rank 3: $1.90M'),
        ('0xa19e640e5644173c99e1104d316bc1c71f958c04', 'Level 1 Rank 4: $1.45M'),
        ('0x287cb2b514af783daec82f0ed81ea812405b6415', 'Level 1 Rank 5: $1.45M'),
        ('0xc90050a8f846a15a7237984df193e548a8ecea11', 'Level 1 Rank 6: $1.43M'),
        ('0xa18900779823a83d46ee5d886fca4f01bf25bdb3', 'Level 1 Rank 7: $1.22M'),
        ('0xb5f1d354abb1b7e50e6fc7fb8d755ee19463dfdb', 'Level 1 Rank 8: $1.08M'),
        ('0xe5014a3e98a41248e8caf751e075a6bd3641b26c', 'Level 1 Rank 9: $1.01M'),
        ('0xcdc1faaf1d8c5c62c1eb781b66b23804880adf5b', 'Level 1 Rank 10: $795K'),
        ('0x2d94dc81f01ead739981f4e1c7c50b3558b506de', 'Level 1 Rank 11: $748K'),
        ('0xc8722078c8918f57cba79bf2be9d1c71d081a99c', 'Level 1 Rank 12: $713K'),
        ('0x008e35f519062ca829093c291eea0938391b8906', 'Level 1 Rank 13: $600K'),
        ('0xb7a932577056e77ad16a9b41d0506ba312c1dbab', 'Level 1 Rank 14: $590K'),
        ('0xe7298eec0c4be60d9a56c06f56ecbd6efdb49eaa', 'Level 1 Rank 15: $545K'),
        ('0x856596b742d85264bf44482faf3f165aeb72a220', 'Level 1 Rank 16: $500K'),
        ('0xbf7bcc73ebd581092bfced976b26dd92833c1642', 'Level 1 Rank 17: $449K'),
        ('0xc06993c6dab487a2573de00dd7a9787f539a8896', 'Level 1 Rank 18: $407K'),
        ('0x88fd8b95cb1b6786a16532fe864f0bc3733bf3dd', 'Level 1 Rank 19: $400K'),
        ('0xabb0914944f36f61ab60802d938b4ce2e713405b', 'Level 1 Rank 20: $363K'),
    ]
    
    # Select addresses based on choice
    if choice == '1':
        addresses_to_check = primary_wallets
    elif choice == '2':
        addresses_to_check = primary_wallets + level1_top20
    elif choice == '3':
        print("\nEnter wallet addresses (one per line, empty line to finish):")
        addresses_to_check = []
        while True:
            addr = input("Address: ").strip()
            if not addr:
                break
            name = input("Name (optional): ").strip()
            addresses_to_check.append((addr, name if name else None))
    else:
        print("Invalid choice")
        return
    
    print(f"\nWill check {len(addresses_to_check)} addresses")
    print(f"Estimated time: {len(addresses_to_check) * 1} - {len(addresses_to_check) * 2} minutes")
    print(f"(Longer than previous version due to transaction history analysis)")
    print()
    
    if input("Continue? (y/n): ").lower() != 'y':
        print("Cancelled")
        return
    
    # Initialize checker
    checker = ImprovedBalanceChecker(api_key)
    
    # Check each address
    results = []
    total_eth = 0
    
    print("\n" + "="*80)
    print("CHECKING BALANCES...")
    print("="*80)
    
    for address, name in addresses_to_check:
        result = checker.check_address(address, name)
        results.append(result)
        total_eth += result['eth_balance']
    
    # Create output directory
    output_dir = Path("balance_reports")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save JSON results
    json_file = output_dir / f'wallet_balances_complete_{timestamp}.json'
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ JSON saved to: {json_file}")
    
    # Create CSV - Summary view (one row per wallet)
    summary_rows = []
    for result in results:
        row = {
            'Address': result['address'],
            'Name': result.get('name', ''),
            'ETH_Balance': result['eth_balance'],
            'Token_Count': len(result['tokens'])
        }
        
        # Add major token balances as columns
        for token in result['tokens']:
            symbol = token['symbol']
            balance = token['balance']
            
            # Add common tokens as their own columns
            if symbol in ['USDC', 'USDT', 'DAI', 'WETH', 'WBTC', 'stETH']:
                row[f'{symbol}_Balance'] = balance
        
        # Calculate approximate USD value (stablecoins)
        stablecoin_value = 0
        for token in result['tokens']:
            if token['symbol'] in ['USDC', 'USDT', 'DAI', 'BUSD', 'GUSD', 'PYUSD']:
                stablecoin_value += token['balance']
        
        row['Stablecoin_Total_USD'] = stablecoin_value
        
        summary_rows.append(row)
    
    summary_df = pd.DataFrame(summary_rows)
    summary_csv = output_dir / f'wallet_balances_summary_{timestamp}.csv'
    summary_df.to_csv(summary_csv, index=False)
    
    print(f"✓ Summary CSV saved to: {summary_csv}")
    
    # Create detailed CSV - All tokens (one row per token per wallet)
    detail_rows = []
    for result in results:
        address = result['address']
        name = result.get('name', '')
        
        # ETH row
        detail_rows.append({
            'Address': address,
            'Name': name,
            'Token_Symbol': 'ETH',
            'Token_Name': 'Ethereum',
            'Token_Contract': 'Native',
            'Balance': result['eth_balance'],
            'Decimals': 18
        })
        
        # Each token as a row
        for token in result['tokens']:
            detail_rows.append({
                'Address': address,
                'Name': name,
                'Token_Symbol': token['symbol'],
                'Token_Name': token['name'],
                'Token_Contract': token['contract'],
                'Balance': token['balance'],
                'Decimals': token['decimals']
            })
    
    detail_df = pd.DataFrame(detail_rows)
    detail_csv = output_dir / f'wallet_balances_detailed_{timestamp}.csv'
    detail_df.to_csv(detail_csv, index=False)
    
    print(f"✓ Detailed CSV saved to: {detail_csv}")
    
    # Create totals summary
    print("\n" + "="*80)
    print("TOTALS ACROSS ALL WALLETS")
    print("="*80)
    
    # Aggregate totals by token symbol
    token_totals = defaultdict(float)
    token_totals['ETH'] = total_eth
    
    for result in results:
        for token in result['tokens']:
            symbol = token['symbol']
            balance = token['balance']
            token_totals[symbol] += balance
    
    # Define stablecoins
    stablecoins = ['USDC', 'USDT', 'DAI', 'BUSD', 'GUSD', 'PYUSD', 'USDD', 'FRAX']
    
    print("\nStablecoins (≈ USD value):")
    stablecoin_total = 0
    for token in stablecoins:
        if token in token_totals and token_totals[token] > 0:
            amount = token_totals[token]
            print(f"  {token}: ${amount:,.2f}")
            stablecoin_total += amount
    
    print(f"\n  TOTAL STABLECOINS: ${stablecoin_total:,.2f}")
    print(f"  *** THIS IS YOUR MINIMUM RECOVERABLE VALUE ***")
    
    print("\nMajor Tokens:")
    major_tokens = ['ETH', 'WETH', 'stETH', 'WBTC']
    for token in major_tokens:
        if token in token_totals and token_totals[token] > 0:
            amount = token_totals[token]
            print(f"  {token}: {amount:,.6f}")
    
    print("\nTop 20 Other Tokens:")
    other_tokens = {k: v for k, v in token_totals.items() 
                   if k not in stablecoins and k not in major_tokens and v > 0}
    
    for i, (token, amount) in enumerate(sorted(other_tokens.items(), 
                                               key=lambda x: x[1], 
                                               reverse=True)[:20]):
        print(f"  {token}: {amount:,.4f}")
    
    if len(other_tokens) > 20:
        print(f"  ... and {len(other_tokens) - 20} more tokens")
    
    # Save totals to CSV
    totals_rows = []
    for token, amount in sorted(token_totals.items(), key=lambda x: x[1], reverse=True):
        is_stablecoin = token in stablecoins
        totals_rows.append({
            'Token': token,
            'Total_Balance': amount,
            'Is_Stablecoin': is_stablecoin,
            'Approx_USD_Value': amount if is_stablecoin else ''
        })
    
    totals_df = pd.DataFrame(totals_rows)
    totals_csv = output_dir / f'wallet_balances_totals_{timestamp}.csv'
    totals_df.to_csv(totals_csv, index=False)
    
    print(f"\n✓ Totals CSV saved to: {totals_csv}")
    
    # Show primary wallet summary
    print("\n" + "="*80)
    print("PRIMARY WALLET BALANCES")
    print("="*80)
    
    for result in results[:6]:  # First 6 are primary
        print(f"\n{result.get('name', 'Unknown')}")
        print(f"  Address: {result['address'][:10]}...{result['address'][-6:]}")
        print(f"  ETH: {result['eth_balance']:.6f}")
        print(f"  Unique tokens: {len(result['tokens'])}")
        
        # Show top 5 tokens
        if result['tokens']:
            print(f"  Top tokens:")
            for token in result['tokens'][:5]:
                print(f"    {token['symbol']}: {token['balance']:,.4f}")
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nAll results saved to: {output_dir}/")
    print(f"\nFiles created:")
    print(f"  1. {json_file.name} - Complete raw data")
    print(f"  2. {summary_csv.name} - Summary view (one row per wallet)")
    print(f"  3. {detail_csv.name} - Detailed view (one row per token)")
    print(f"  4. {totals_csv.name} - Aggregate totals by token")
    print(f"\nThis shows ALL tokens based on transaction history.")
    print(f"Compare with Etherscan to verify accuracy.")


if __name__ == "__main__":
    main()
