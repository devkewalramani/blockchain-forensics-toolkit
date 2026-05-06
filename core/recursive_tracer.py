#!/usr/bin/env python3
"""
Advanced Blockchain Forensics - Recursive Fund Tracing
Follows money through multiple layers (hops) to find ultimate destinations

WARNING: This can make THOUSANDS of API calls. Use carefully!
"""

import sys
import json
from pathlib import Path
from goliath_forensics import EtherscanAPI, WalletAnalyzer, ReportGenerator
import logging
from typing import Dict, List, Set, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class RecursiveTracer:
    """Recursively traces funds through wallet networks"""
    
    def __init__(self, api: EtherscanAPI, max_depth: int = 3, min_amount: float = 1000):
        """
        Initialize recursive tracer
        
        Args:
            api: Etherscan API instance
            max_depth: Maximum hops to trace (default 3)
            min_amount: Minimum USDC amount to trace (default $1,000)
        """
        self.api = api
        self.wallet_analyzer = WalletAnalyzer(api)
        self.max_depth = max_depth
        self.min_amount = min_amount
        self.traced_wallets = {}  # Cache of analyzed wallets
        self.trace_tree = {}  # Tree structure of fund flows
        
    def trace_funds(self, source_addresses: List[str], source_names: Dict[str, str] = None) -> Dict:
        """
        Trace funds from source wallets through multiple hops
        
        Args:
            source_addresses: List of starting wallet addresses
            source_names: Optional dict of {address: name}
            
        Returns:
            Complete trace results with multi-level analysis
        """
        source_names = source_names or {}
        
        logger.info(f"\n{'='*80}")
        logger.info(f"RECURSIVE FUND TRACING - {len(source_addresses)} SOURCE WALLETS")
        logger.info(f"Max Depth: {self.max_depth} hops | Min Amount: ${self.min_amount:,.0f}")
        logger.info(f"{'='*80}\n")
        
        # Level 0: Source wallets (already known)
        logger.info("LEVEL 0: Analyzing source wallets...")
        for addr in source_addresses:
            name = source_names.get(addr, f"Source_{addr[:10]}")
            self._analyze_and_cache(addr, name, level=0)
        
        # Trace through multiple levels
        for level in range(1, self.max_depth + 1):
            logger.info(f"\nLEVEL {level}: Tracing recipients from previous level...")
            self._trace_level(level)
        
        # Analyze results
        analysis = self._compile_analysis(source_addresses)
        
        return analysis
    
    def _analyze_and_cache(self, address: str, name: str, level: int) -> Dict:
        """Analyze wallet and cache results"""
        addr_lower = address.lower()
        
        # Check cache first
        if addr_lower in self.traced_wallets:
            logger.info(f"  [CACHED] {name}")
            return self.traced_wallets[addr_lower]
        
        # Analyze wallet
        analysis = self.wallet_analyzer.analyze_wallet(address, name)
        analysis['trace_level'] = level
        
        # Cache it
        self.traced_wallets[addr_lower] = analysis
        
        return analysis
    
    def _trace_level(self, level: int):
        """Trace one level of recipients"""
        
        # Get all wallets from previous level
        prev_level_wallets = [
            addr for addr, analysis in self.traced_wallets.items()
            if analysis.get('trace_level') == level - 1
        ]
        
        if not prev_level_wallets:
            logger.warning(f"No wallets found at level {level-1}. Stopping trace.")
            return
        
        logger.info(f"Analyzing {len(prev_level_wallets)} wallets from level {level-1}...")
        
        # Find all unique receivers from previous level
        next_level_candidates = set()
        
        for source_addr in prev_level_wallets:
            source_analysis = self.traced_wallets[source_addr]
            
            # Add top receivers that received >= min_amount
            for receiver_addr, amount in source_analysis['top_receivers']:
                if amount >= self.min_amount:
                    receiver_lower = receiver_addr.lower()
                    
                    # Skip if already traced
                    if receiver_lower not in self.traced_wallets:
                        next_level_candidates.add((receiver_lower, amount))
        
        # Sort by amount (trace largest first)
        sorted_candidates = sorted(next_level_candidates, key=lambda x: x[1], reverse=True)
        
        logger.info(f"Found {len(sorted_candidates)} new addresses at level {level}")
        logger.info(f"  (Filtering: received >= ${self.min_amount:,.0f})")
        
        # Limit to prevent explosion (optional safety)
        MAX_PER_LEVEL = 50
        if len(sorted_candidates) > MAX_PER_LEVEL:
            logger.warning(f"Limiting to top {MAX_PER_LEVEL} addresses by volume")
            sorted_candidates = sorted_candidates[:MAX_PER_LEVEL]
        
        # Analyze each candidate
        for i, (addr, amount) in enumerate(sorted_candidates, 1):
            name = f"L{level}_Recipient_{i}"
            logger.info(f"  [{i}/{len(sorted_candidates)}] {addr[:10]}... (${amount:,.0f})")
            
            try:
                self._analyze_and_cache(addr, name, level)
            except Exception as e:
                logger.error(f"  Failed to analyze {addr}: {e}")
                continue
    
    def _compile_analysis(self, source_addresses: List[str]) -> Dict:
        """Compile final analysis from traced data"""
        
        logger.info(f"\n{'='*80}")
        logger.info("COMPILING FINAL ANALYSIS...")
        logger.info(f"{'='*80}\n")
        
        # Organize by level
        by_level = {}
        for addr, analysis in self.traced_wallets.items():
            level = analysis.get('trace_level', 0)
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(analysis)
        
        # Calculate statistics
        total_wallets = len(self.traced_wallets)
        total_volume = sum(a['total_usdc_sent'] for a in self.traced_wallets.values())
        
        # Find terminal addresses (no further outgoing traced)
        terminal_addresses = []
        for addr, analysis in self.traced_wallets.items():
            if analysis.get('trace_level') == self.max_depth:
                terminal_addresses.append({
                    'address': addr,
                    'name': analysis['name'],
                    'total_received': analysis['total_usdc_received'],
                    'classification': analysis['classification']
                })
        
        terminal_addresses.sort(key=lambda x: x['total_received'], reverse=True)
        
        # Build trace paths (source -> ... -> destination)
        trace_paths = self._build_trace_paths(source_addresses)
        
        analysis = {
            'config': {
                'max_depth': self.max_depth,
                'min_amount': self.min_amount,
                'source_wallets': len(source_addresses)
            },
            'summary': {
                'total_wallets_traced': total_wallets,
                'total_volume_traced': total_volume,
                'wallets_by_level': {level: len(wallets) for level, wallets in by_level.items()}
            },
            'by_level': by_level,
            'terminal_addresses': terminal_addresses,
            'trace_paths': trace_paths,
            'all_wallet_data': self.traced_wallets,
            'timestamp': datetime.now().isoformat()
        }
        
        # Log summary
        logger.info(f"Total Wallets Traced: {total_wallets}")
        logger.info(f"Total Volume: ${total_volume:,.2f}")
        for level, wallets in sorted(by_level.items()):
            logger.info(f"  Level {level}: {len(wallets)} wallets")
        logger.info(f"Terminal Addresses (Level {self.max_depth}): {len(terminal_addresses)}")
        
        return analysis
    
    def _build_trace_paths(self, source_addresses: List[str]) -> List[Dict]:
        """Build complete paths from source to destination"""
        # This is complex - simplified version
        # Full implementation would build complete directed graph
        
        paths = []
        # For now, just identify high-value terminal destinations
        
        for source in source_addresses:
            source_lower = source.lower()
            if source_lower in self.traced_wallets:
                source_analysis = self.traced_wallets[source_lower]
                
                # Top 10 destinations from this source
                for receiver_addr, amount in source_analysis['top_receivers'][:10]:
                    paths.append({
                        'source': source_lower,
                        'destination': receiver_addr,
                        'amount': amount,
                        'path_type': 'direct'
                    })
        
        return paths


class AdvancedReportGenerator(ReportGenerator):
    """Enhanced report generator for recursive analysis"""
    
    def generate_recursive_report(self, trace_analysis: Dict, case_name: str = "Goliath_Recursive"):
        """Generate reports for recursive trace analysis"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Executive Summary
        summary_file = self.output_dir / f"{case_name}_Trace_Summary_{timestamp}.txt"
        self._write_trace_summary(trace_analysis, summary_file)
        
        # 2. Terminal Addresses (ultimate destinations)
        terminal_csv = self.output_dir / f"{case_name}_Terminal_Addresses_{timestamp}.csv"
        self._write_terminal_addresses(trace_analysis, terminal_csv)
        
        # 3. By-Level Analysis
        for level, wallets in trace_analysis['by_level'].items():
            level_csv = self.output_dir / f"{case_name}_Level{level}_Wallets_{timestamp}.csv"
            self._write_level_analysis(wallets, level_csv)
        
        # 4. Complete JSON dump
        json_file = self.output_dir / f"{case_name}_Complete_Trace_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(trace_analysis, f, indent=2, default=str)
        
        logger.info(f"\n{'='*80}")
        logger.info("RECURSIVE TRACE REPORTS GENERATED")
        logger.info(f"{'='*80}")
        logger.info(f"Summary: {summary_file}")
        logger.info(f"Terminal Addresses: {terminal_csv}")
        logger.info(f"Complete Data: {json_file}")
        
        return {
            'summary': summary_file,
            'terminal': terminal_csv,
            'raw_data': json_file
        }
    
    def _write_trace_summary(self, analysis: Dict, filepath: Path):
        """Write recursive trace summary"""
        with open(filepath, 'w') as f:
            f.write("="*80 + "\n")
            f.write("RECURSIVE FUND TRACING - EXECUTIVE SUMMARY\n")
            f.write("="*80 + "\n\n")
            
            config = analysis['config']
            summary = analysis['summary']
            
            f.write(f"Trace Configuration:\n")
            f.write(f"  Source Wallets: {config['source_wallets']}\n")
            f.write(f"  Maximum Depth: {config['max_depth']} hops\n")
            f.write(f"  Minimum Amount: ${config['min_amount']:,.0f}\n\n")
            
            f.write(f"Results:\n")
            f.write(f"  Total Wallets Traced: {summary['total_wallets_traced']}\n")
            f.write(f"  Total Volume: ${summary['total_volume_traced']:,.2f}\n\n")
            
            f.write("Wallets by Level:\n")
            for level, count in sorted(summary['wallets_by_level'].items()):
                f.write(f"  Level {level}: {count} wallets\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write("TOP TERMINAL ADDRESSES (Ultimate Destinations)\n")
            f.write("="*80 + "\n\n")
            
            for i, terminal in enumerate(analysis['terminal_addresses'][:30], 1):
                f.write(f"{i}. {terminal['address']}\n")
                f.write(f"   Received: ${terminal['total_received']:,.2f}\n")
                f.write(f"   Classification: {terminal['classification']}\n")
                f.write(f"   ** CRITICAL: SUBPOENA FOR KYC **\n\n")
    
    def _write_terminal_addresses(self, analysis: Dict, filepath: Path):
        """Write terminal addresses CSV"""
        import pandas as pd
        
        rows = []
        for i, terminal in enumerate(analysis['terminal_addresses'], 1):
            rows.append({
                'Rank': i,
                'Address': terminal['address'],
                'Name': terminal['name'],
                'Total_Received_USDC': terminal['total_received'],
                'Classification': terminal['classification'],
                'Trace_Level': self.max_depth if hasattr(self, 'max_depth') else 'N/A',
                'Priority': 'CRITICAL' if i <= 20 else 'HIGH' if i <= 50 else 'MEDIUM',
                'Action': 'SUBPOENA EXCHANGES - LIKELY CASH-OUT POINT'
            })
        
        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False)
    
    def _write_level_analysis(self, wallets: List[Dict], filepath: Path):
        """Write per-level wallet analysis"""
        import pandas as pd
        
        rows = []
        for wallet in wallets:
            rows.append({
                'Address': wallet['address'],
                'Name': wallet['name'],
                'Classification': wallet['classification'],
                'USDC_Received': wallet['total_usdc_received'],
                'USDC_Sent': wallet['total_usdc_sent'],
                'Net_Flow': wallet['net_flow'],
                'Transactions_In': wallet['incoming_count'],
                'Transactions_Out': wallet['outgoing_count']
            })
        
        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False)


def main():
    """Main execution for recursive tracing"""
    
    print("="*80)
    print("ADVANCED RECURSIVE FUND TRACING")
    print("="*80)
    print()
    print("WARNING: This can make THOUSANDS of API calls!")
    print("Recommended: Use with Etherscan API key")
    print()
    
    # Get configuration
    api_key = input("Enter Etherscan API Key: ").strip()
    if not api_key:
        print("ERROR: API key strongly recommended for recursive tracing")
        if input("Continue without key? (y/n): ").lower() != 'y':
            return
    
    max_depth = int(input("Maximum trace depth (1-4, recommended 3): ") or "3")
    min_amount = float(input("Minimum amount to trace in USD (recommended 1000): ") or "1000")
    
    # Initialize
    api = EtherscanAPI(api_key)
    tracer = RecursiveTracer(api, max_depth=max_depth, min_amount=min_amount)
    
    # Goliath source wallets
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
    
    print(f"\nTracing funds from {len(source_wallets)} Goliath wallets...")
    print(f"This may take 30-60+ minutes...")
    print()
    
    # Confirm
    if input("Start recursive trace? (y/n): ").lower() != 'y':
        print("Cancelled")
        return
    
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
    print("="*80)


if __name__ == "__main__":
    main()
