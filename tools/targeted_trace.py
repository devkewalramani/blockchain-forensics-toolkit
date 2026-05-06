#!/usr/bin/env python3
"""
Targeted Deep Trace - Flexible Wallet Analysis
Allows specifying any wallet addresses for deep recursive tracing

Use this for selective deep dives on specific addresses of interest
"""

import sys
from pathlib import Path
from goliath_forensics import EtherscanAPI, WalletAnalyzer
from recursive_tracer import RecursiveTracer, AdvancedReportGenerator
import logging

logger = logging.getLogger(__name__)


def get_wallet_addresses_interactive():
    """Get wallet addresses from user interactively"""
    
    print("\n" + "="*80)
    print("TARGETED DEEP TRACE - WALLET INPUT")
    print("="*80)
    print()
    print("Enter wallet addresses to trace (one per line)")
    print("Press Enter on empty line when done")
    print()
    print("You can also specify a name for each wallet:")
    print("  FORMAT: address,name")
    print("  EXAMPLE: 0x1234...abcd,Punit Shah Wallet")
    print()
    print("Or just the address:")
    print("  EXAMPLE: 0x1234...abcd")
    print()
    
    wallets = {}
    counter = 1
    
    while True:
        line = input(f"Wallet {counter}: ").strip()
        
        if not line:
            break
        
        # Parse input
        if ',' in line:
            address, name = line.split(',', 1)
            address = address.strip()
            name = name.strip()
        else:
            address = line.strip()
            name = f"Target_Wallet_{counter}"
        
        # Basic validation
        if not address.startswith('0x') or len(address) != 42:
            print(f"  ⚠️  Invalid address format: {address}")
            print("  Address should start with 0x and be 42 characters")
            continue
        
        wallets[address.lower()] = name
        print(f"  ✓ Added: {name} ({address[:10]}...)")
        counter += 1
    
    return wallets


def get_wallet_addresses_from_file(filepath):
    """Load wallet addresses from a file"""
    
    print(f"\nLoading wallets from: {filepath}")
    
    wallets = {}
    
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse line
            if ',' in line:
                address, name = line.split(',', 1)
                address = address.strip()
                name = name.strip()
            else:
                address = line.strip()
                name = f"Wallet_{i}"
            
            # Validate
            if address.startswith('0x') and len(address) == 42:
                wallets[address.lower()] = name
                print(f"  ✓ Loaded: {name} ({address[:10]}...)")
            else:
                print(f"  ⚠️  Skipped invalid address on line {i}: {address}")
        
        print(f"\nLoaded {len(wallets)} valid addresses")
        
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}")
        return None
    except Exception as e:
        print(f"ERROR reading file: {e}")
        return None
    
    return wallets


def main():
    """Main execution"""
    
    print("="*80)
    print("TARGETED DEEP TRACE - FLEXIBLE WALLET ANALYSIS")
    print("="*80)
    print()
    print("This tool traces specific wallets through multiple transaction levels")
    print("to find ultimate destinations and cash-out points.")
    print()
    
    # Get API key
    api_key = input("Enter Etherscan API Key (or press Enter to use default): ").strip()
    if not api_key:
        # Try to load from environment or config
        api_key = "92HEGKG3JKMDEUIA7H3WASI8W5CSWEX2R1"  # Your key
        print(f"Using configured API key")
    
    # Get wallet addresses
    print()
    print("How would you like to provide wallet addresses?")
    print()
    print("1. Enter manually (interactive)")
    print("2. Load from file")
    print()
    
    choice = input("Choice (1 or 2): ").strip()
    
    if choice == "1":
        wallets = get_wallet_addresses_interactive()
    elif choice == "2":
        filepath = input("Enter file path: ").strip()
        wallets = get_wallet_addresses_from_file(filepath)
        if wallets is None:
            return
    else:
        print("Invalid choice")
        return
    
    if not wallets:
        print("\nNo wallets provided. Exiting.")
        return
    
    print()
    print("="*80)
    print(f"ANALYZING {len(wallets)} WALLET(S)")
    print("="*80)
    for addr, name in wallets.items():
        print(f"  • {name}: {addr[:10]}...{addr[-6:]}")
    
    # Get trace parameters
    print()
    print("="*80)
    print("TRACE PARAMETERS")
    print("="*80)
    print()
    
    max_depth = input("Maximum trace depth (1-5, recommended 3-4): ").strip()
    max_depth = int(max_depth) if max_depth else 3
    
    min_amount = input("Minimum amount to trace in USD (recommended 1000): ").strip()
    min_amount = float(min_amount) if min_amount else 1000
    
    print()
    print(f"Configuration:")
    print(f"  Wallets: {len(wallets)}")
    print(f"  Max Depth: {max_depth} hops")
    print(f"  Min Amount: ${min_amount:,.0f}")
    print()
    
    # Estimate API calls
    estimated_calls = len(wallets) * 5 * (max_depth + 1)
    print(f"Estimated API calls: {estimated_calls} - {estimated_calls * 2}")
    print(f"Estimated time: {estimated_calls // 60} - {estimated_calls // 30} minutes")
    print()
    
    if input("Start targeted trace? (y/n): ").lower() != 'y':
        print("Cancelled")
        return
    
    # Initialize
    print("\nInitializing...")
    api = EtherscanAPI(api_key)
    tracer = RecursiveTracer(api, max_depth=max_depth, min_amount=min_amount)
    
    # Execute trace
    print("\nStarting recursive trace...")
    print("This may take a while depending on transaction volume.\n")
    
    trace_results = tracer.trace_funds(list(wallets.keys()), wallets)
    
    # Generate reports
    print("\nGenerating reports...")
    report_gen = AdvancedReportGenerator()
    
    # Create custom case name
    if len(wallets) == 1:
        case_name = f"Targeted_{list(wallets.values())[0].replace(' ', '_')}"
    else:
        case_name = f"Targeted_{len(wallets)}_Wallets"
    
    reports = report_gen.generate_recursive_report(trace_results, case_name)
    
    # Summary
    print("\n" + "="*80)
    print("TARGETED TRACE COMPLETE!")
    print("="*80)
    print(f"\nWallets Analyzed: {len(wallets)}")
    print(f"Total Network Traced: {trace_results['summary']['total_wallets_traced']} addresses")
    print(f"API Calls Made: {api.call_count}")
    print(f"\nReports saved to: ./reports/")
    print()
    
    # Show top findings
    print("TOP 10 TERMINAL ADDRESSES (Ultimate Destinations):")
    print("-"*80)
    for i, terminal in enumerate(trace_results['terminal_addresses'][:10], 1):
        print(f"{i}. {terminal['address'][:10]}...{terminal['address'][-6:]}")
        print(f"   Received: ${terminal['total_received']:,.0f}")
        print(f"   Classification: {terminal['classification']}")
    
    print("\n" + "="*80)
    print("Review detailed reports in ./reports/ directory")
    print("="*80)


def load_from_csv(csv_file):
    """Helper to load addresses from CSV export"""
    import pandas as pd
    
    print(f"Loading addresses from CSV: {csv_file}")
    
    try:
        df = pd.read_csv(csv_file)
        
        # Assume first column is address
        address_col = df.columns[0]
        
        wallets = {}
        for idx, row in df.iterrows():
            address = row[address_col]
            
            # Try to get a name from other columns
            if 'Name' in df.columns:
                name = row['Name']
            elif len(df.columns) > 1:
                name = f"{df.columns[1]}_{row[df.columns[1]]}"
            else:
                name = f"CSV_Wallet_{idx+1}"
            
            wallets[address.lower()] = name
        
        print(f"Loaded {len(wallets)} addresses from CSV")
        return wallets
        
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None


if __name__ == "__main__":
    # Check if CSV file provided as argument
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        wallets = load_from_csv(csv_file)
        
        if wallets:
            print(f"\nLoaded {len(wallets)} wallets from {csv_file}")
            
            # Get API key
            api_key = "92HEGKG3JKMDEUIA7H3WASI8W5CSWEX2R1"
            
            # Get parameters
            max_depth = int(input("Max depth (3-5): ") or "3")
            min_amount = float(input("Min amount ($): ") or "1000")
            
            if input("Start trace? (y/n): ").lower() == 'y':
                api = EtherscanAPI(api_key)
                tracer = RecursiveTracer(api, max_depth=max_depth, min_amount=min_amount)
                
                trace_results = tracer.trace_funds(list(wallets.keys()), wallets)
                
                report_gen = AdvancedReportGenerator()
                case_name = Path(csv_file).stem
                reports = report_gen.generate_recursive_report(trace_results, case_name)
                
                print(f"\nComplete! API calls: {api.call_count}")
    else:
        main()
