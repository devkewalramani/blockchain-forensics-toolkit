#!/usr/bin/env python3
"""
Quick Start Launcher for Goliath Forensics
Pre-configured with API key - just run it!
"""

import os
import sys

# Your Etherscan API Key (pre-configured)
ETHERSCAN_API_KEY = "92HEGKG3JKMDEUIA7H3WASI8W5CSWEX2R1"

print("="*80)
print("GOLIATH VENTURES - BLOCKCHAIN FORENSICS")
print("Quick Start Launcher")
print("="*80)
print()
print("Select analysis type:")
print()
print("1. BASIC NETWORK ANALYSIS (Recommended - Start Here)")
print("   - Analyzes all 5 Goliath wallets")
print("   - Identifies top receiving addresses for subpoenas")
print("   - Runtime: 10-20 minutes")
print("   - API calls: ~500")
print()
print("2. RECURSIVE FUND TRACING (Advanced - Run After Basic)")
print("   - Traces funds through multiple hops")
print("   - Finds ultimate cash-out destinations")
print("   - Runtime: 30-60 minutes")
print("   - API calls: 1,000-2,000")
print()

choice = input("Enter choice (1 or 2): ").strip()

if choice == "1":
    print("\nLaunching Basic Network Analysis...")
    print("Your API key is pre-configured.")
    print()
    
    # Import and run basic analysis with API key
    from goliath_forensics import EtherscanAPI, NetworkAnalyzer, ReportGenerator
    
    # Initialize with your API key
    api = EtherscanAPI(ETHERSCAN_API_KEY)
    
    # Known Goliath wallets
    goliath_wallets = {
        "0xdDBae474cD6e7DA39555d71a61e9794822c57968": "Goliath Wallet 1 - Distribution",
        "0xC37A3bb2F061C002f8127ba1E25402193dce862F": "Goliath Wallet 2 - Distribution",
        "0x77696bb39917C91A0c3908D577d5e322095425cA": "Goliath Wallet 3",
        "0x808b4dA0Be6c9512E948521452227EFc619BeA52": "Goliath Wallet 4",
        "0xd24400ae8BfEBb18cA49Be86258a3C749cf46853": "Goliath Wallet 5"
    }
    
    print(f"Analyzing {len(goliath_wallets)} Goliath wallets...")
    print("This will take approximately 10-20 minutes.")
    print()
    
    # Confirm
    if input("Start analysis? (y/n): ").lower() != 'y':
        print("Cancelled")
        sys.exit(0)
    
    # Analyze network
    network_analyzer = NetworkAnalyzer(api)
    network_analysis = network_analyzer.analyze_network(goliath_wallets)
    
    # Generate reports
    print("\nGenerating prosecutor reports...")
    report_gen = ReportGenerator()
    reports = report_gen.generate_prosecutor_report(network_analysis)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print(f"Total API calls made: {api.call_count}")
    print(f"Reports saved to: ./reports/")
    print()
    print("NEXT STEPS:")
    print("1. Review reports/Goliath_Executive_Summary_*.txt")
    print("2. Share reports/Goliath_Top_Receivers_SUBPOENA_*.csv with prosecutors")
    print("3. Consider running Recursive Trace (option 2) for deeper analysis")
    print("="*80)

elif choice == "2":
    print("\nLaunching Recursive Fund Tracing...")
    print("Your API key is pre-configured.")
    print()
    
    # Get configuration
    max_depth = input("Maximum trace depth (1-4, default 3): ").strip()
    max_depth = int(max_depth) if max_depth else 3
    
    min_amount = input("Minimum amount to trace in USD (default 1000): ").strip()
    min_amount = float(min_amount) if min_amount else 1000
    
    print()
    print(f"Configuration:")
    print(f"  Max Depth: {max_depth} hops")
    print(f"  Min Amount: ${min_amount:,.0f}")
    print()
    print("WARNING: This will make 1,000-2,000+ API calls")
    print("Estimated time: 30-60 minutes")
    print()
    
    if input("Start recursive trace? (y/n): ").lower() != 'y':
        print("Cancelled")
        sys.exit(0)
    
    # Import and run recursive analysis
    from goliath_forensics import EtherscanAPI
    from recursive_tracer import RecursiveTracer, AdvancedReportGenerator
    
    # Initialize
    api = EtherscanAPI(ETHERSCAN_API_KEY)
    tracer = RecursiveTracer(api, max_depth=max_depth, min_amount=min_amount)
    
    # Source wallets
    source_wallets = [
        "0xdDBae474cD6e7DA39555d71a61e9794822c57968",
        "0xC37A3bb2F061C002f8127ba1E25402193dce862F",
        "0x77696bb39917C91A0c3908D577d5e322095425cA",
        "0x808b4dA0Be6c9512E948521452227EFc619BeA52",
        "0xd24400ae8BfEBb18cA49Be86258a3C749cf46853"
    ]
    
    source_names = {
        source_wallets[0]: "Goliath_Dist_1",
        source_wallets[1]: "Goliath_Dist_2",
        source_wallets[2]: "Goliath_W3",
        source_wallets[3]: "Goliath_W4",
        source_wallets[4]: "Goliath_W5"
    }
    
    # Execute trace
    trace_results = tracer.trace_funds(source_wallets, source_names)
    
    # Generate reports
    print("\nGenerating reports...")
    report_gen = AdvancedReportGenerator()
    reports = report_gen.generate_recursive_report(trace_results)
    
    print("\n" + "="*80)
    print("RECURSIVE TRACE COMPLETE!")
    print("="*80)
    print(f"API Calls Made: {api.call_count}")
    print(f"Wallets Traced: {trace_results['summary']['total_wallets_traced']}")
    print(f"Reports in: ./reports/")
    print()
    print("CRITICAL FILE:")
    print("  reports/Goliath_Recursive_Terminal_Addresses_*.csv")
    print("  ^ These are ULTIMATE DESTINATIONS - highest priority subpoenas")
    print("="*80)

else:
    print("Invalid choice. Exiting.")
    sys.exit(1)
