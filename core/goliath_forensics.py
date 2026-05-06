#!/usr/bin/env python3
"""
Goliath Ventures - Blockchain Forensic Analysis Tool
Investigates wallet networks and traces fund flows for DOJ/FBI/SEC

RESPECTS ETHERSCAN API LIMITS:
- 5 calls/second (0.2s sleep between calls)
- 1,000 records per call (automatic pagination)
- 100,000 calls/day (progress tracking)
"""

import requests
import time
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Optional, Set
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('forensics.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class EtherscanAPI:
    """Wrapper for Etherscan API with rate limiting and caching"""
    
    BASE_URL = "https://api.etherscan.io/v2/api"  # V2 endpoint
    RATE_LIMIT_DELAY = 0.21  # Slightly over 0.2s to be safe (5 calls/sec)
    MAX_RECORDS_PER_CALL = 1000
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Etherscan API client
        
        Args:
            api_key: Etherscan API key (optional, but recommended)
        """
        self.api_key = api_key or "YourApiKeyToken"  # Free tier works without key
        self.last_call_time = 0
        self.call_count = 0
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        
    def _rate_limit(self):
        """Enforce rate limiting (5 calls/sec)"""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.RATE_LIMIT_DELAY:
            sleep_time = self.RATE_LIMIT_DELAY - elapsed
            time.sleep(sleep_time)
        self.last_call_time = time.time()
        self.call_count += 1
        
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path for a given key"""
        return self.cache_dir / f"{cache_key}.json"
    
    def _load_cache(self, cache_key: str) -> Optional[Dict]:
        """Load data from cache if it exists"""
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded from cache: {cache_key}")
                    return data
            except Exception as e:
                logger.warning(f"Cache read error for {cache_key}: {e}")
        return None
    
    def _save_cache(self, cache_key: str, data: Dict):
        """Save data to cache"""
        cache_path = self._get_cache_path(cache_key)
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.warning(f"Cache write error for {cache_key}: {e}")
    
    def _make_request(self, params: Dict, cache_key: Optional[str] = None) -> Dict:
        """
        Make API request with rate limiting and caching
        
        Args:
            params: API parameters
            cache_key: Optional cache key (skips API call if cached)
            
        Returns:
            API response as dict
        """
        # Check cache first
        if cache_key:
            cached = self._load_cache(cache_key)
            if cached is not None:
                return cached
        
        # Add API key and chainid for V2
        params['apikey'] = self.api_key
        params['chainid'] = '1'  # Ethereum mainnet
        
        # Rate limit
        self._rate_limit()
        
        # Make request
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if data.get('status') == '0' and data.get('message') != 'No transactions found':
                logger.error(f"API Error: {data.get('message')} - {data.get('result')}")
            
            # Cache successful response
            if cache_key and data.get('status') == '1':
                self._save_cache(cache_key, data)
            
            logger.info(f"API call #{self.call_count}: {params.get('module')}.{params.get('action')}")
            return data
            
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {'status': '0', 'message': str(e), 'result': []}
    
    def get_token_transfers(self, address: str, contract_address: str = None,
                           start_block: int = 0, end_block: int = 99999999,
                           page: int = 1, offset: int = 1000) -> List[Dict]:
        """
        Get ERC20 token transfer events for an address
        
        Args:
            address: Wallet address
            contract_address: Optional - filter by token contract (e.g., USDC)
            start_block: Starting block number
            end_block: Ending block number
            page: Page number for pagination
            offset: Number of records per page (max 1000)
            
        Returns:
            List of token transfer transactions
        """
        params = {
            'module': 'account',
            'action': 'tokentx',
            'address': address,
            'startblock': start_block,
            'endblock': end_block,
            'page': page,
            'offset': min(offset, self.MAX_RECORDS_PER_CALL),
            'sort': 'desc'
        }
        
        if contract_address:
            params['contractaddress'] = contract_address
        
        cache_key = f"tokentx_{address}_{contract_address or 'all'}_{page}"
        response = self._make_request(params, cache_key)
        
        result = response.get('result', [])
        
        # Handle case where result is a string (error message)
        if isinstance(result, str):
            logger.warning(f"API returned string instead of list: {result}")
            return []
        
        return result
    
    def get_all_token_transfers(self, address: str, contract_address: str = None) -> List[Dict]:
        """
        Get ALL token transfers for an address (handles pagination automatically)
        
        Args:
            address: Wallet address
            contract_address: Optional token contract filter
            
        Returns:
            Complete list of all token transfers
        """
        all_transfers = []
        page = 1
        
        logger.info(f"Fetching token transfers for {address[:10]}...")
        
        while True:
            transfers = self.get_token_transfers(address, contract_address, page=page)
            
            if not transfers or transfers == []:
                break
                
            all_transfers.extend(transfers)
            logger.info(f"  Page {page}: {len(transfers)} transactions (total: {len(all_transfers)})")
            
            # If we got less than max, we're done
            if len(transfers) < self.MAX_RECORDS_PER_CALL:
                break
                
            page += 1
        
        logger.info(f"Total transfers for {address[:10]}: {len(all_transfers)}")
        return all_transfers
    
    def get_normal_transactions(self, address: str, page: int = 1, offset: int = 1000) -> List[Dict]:
        """Get normal ETH transactions for an address"""
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': 0,
            'endblock': 99999999,
            'page': page,
            'offset': min(offset, self.MAX_RECORDS_PER_CALL),
            'sort': 'desc'
        }
        
        cache_key = f"txlist_{address}_{page}"
        response = self._make_request(params, cache_key)
        
        return response.get('result', [])
    
    def get_balance(self, address: str) -> float:
        """Get current ETH balance for an address"""
        params = {
            'module': 'account',
            'action': 'balance',
            'address': address,
            'tag': 'latest'
        }
        
        response = self._make_request(params)
        balance_wei = int(response.get('result', 0))
        return balance_wei / 1e18  # Convert Wei to ETH


class WalletAnalyzer:
    """Analyzes individual wallet activity"""
    
    # USDC contract address on Ethereum mainnet
    USDC_CONTRACT = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    
    def __init__(self, api: EtherscanAPI):
        self.api = api
    
    def analyze_wallet(self, address: str, name: str = None) -> Dict:
        """
        Comprehensive analysis of a single wallet
        
        Args:
            address: Wallet address
            name: Optional friendly name
            
        Returns:
            Analysis results as dict
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"ANALYZING WALLET: {name or address}")
        logger.info(f"{'='*80}\n")
        
        # Get all token transfers (focusing on USDC)
        usdc_transfers = self.api.get_all_token_transfers(address, self.USDC_CONTRACT)
        
        # Separate incoming and outgoing
        incoming = [tx for tx in usdc_transfers if tx['to'].lower() == address.lower()]
        outgoing = [tx for tx in usdc_transfers if tx['from'].lower() == address.lower()]
        
        # Calculate volumes (USDC has 6 decimals)
        total_received = sum(int(tx['value']) / 1e6 for tx in incoming)
        total_sent = sum(int(tx['value']) / 1e6 for tx in outgoing)
        
        # Find unique counterparties
        senders = set(tx['from'].lower() for tx in incoming)
        receivers = set(tx['to'].lower() for tx in outgoing)
        
        # Top counterparties by volume
        sender_volumes = {}
        for tx in incoming:
            sender = tx['from'].lower()
            sender_volumes[sender] = sender_volumes.get(sender, 0) + int(tx['value']) / 1e6
        
        receiver_volumes = {}
        for tx in outgoing:
            receiver = tx['to'].lower()
            receiver_volumes[receiver] = receiver_volumes.get(receiver, 0) + int(tx['value']) / 1e6
        
        top_senders = sorted(sender_volumes.items(), key=lambda x: x[1], reverse=True)[:10]
        top_receivers = sorted(receiver_volumes.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Transaction timing analysis
        dates = []
        for tx in usdc_transfers:
            try:
                timestamp = int(tx['timeStamp'])
                dates.append(datetime.fromtimestamp(timestamp))
            except:
                pass
        
        analysis = {
            'address': address,
            'name': name or address[:10],
            'total_usdc_received': total_received,
            'total_usdc_sent': total_sent,
            'net_flow': total_received - total_sent,
            'incoming_count': len(incoming),
            'outgoing_count': len(outgoing),
            'unique_senders': len(senders),
            'unique_receivers': len(receivers),
            'top_senders': top_senders,
            'top_receivers': top_receivers,
            'first_activity': min(dates) if dates else None,
            'last_activity': max(dates) if dates else None,
            'all_transfers': usdc_transfers,
            'classification': self._classify_wallet(len(incoming), len(outgoing))
        }
        
        # Log summary
        logger.info(f"Classification: {analysis['classification']}")
        logger.info(f"USDC Received: ${total_received:,.2f} ({len(incoming)} txns)")
        logger.info(f"USDC Sent: ${total_sent:,.2f} ({len(outgoing)} txns)")
        logger.info(f"Net Flow: ${analysis['net_flow']:,.2f}")
        logger.info(f"Unique Senders: {len(senders)}")
        logger.info(f"Unique Receivers: {len(receivers)}")
        
        if dates:
            logger.info(f"Activity Range: {min(dates)} to {max(dates)}")
        
        return analysis
    
    def _classify_wallet(self, incoming: int, outgoing: int) -> str:
        """Classify wallet based on transaction patterns"""
        total = incoming + outgoing
        if total == 0:
            return "INACTIVE"
        
        outgoing_pct = outgoing / total
        
        if outgoing_pct > 0.9:
            return "DISTRIBUTION (Ponzi Payout)"
        elif outgoing_pct > 0.7:
            return "PRIMARILY OUTGOING (Likely Distribution)"
        elif outgoing_pct > 0.3:
            return "MIXED (Operational)"
        elif outgoing_pct > 0.1:
            return "PRIMARILY INCOMING (Collection)"
        else:
            return "COLLECTION (Investor Deposits)"


class NetworkAnalyzer:
    """Analyzes networks of connected wallets"""
    
    def __init__(self, api: EtherscanAPI):
        self.api = api
        self.wallet_analyzer = WalletAnalyzer(api)
    
    def analyze_network(self, wallet_addresses: Dict[str, str]) -> Dict:
        """
        Analyze a network of wallets and their connections
        
        Args:
            wallet_addresses: Dict of {address: name}
            
        Returns:
            Network analysis results
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"NETWORK ANALYSIS - {len(wallet_addresses)} WALLETS")
        logger.info(f"{'='*80}\n")
        
        # Analyze each wallet
        wallet_analyses = {}
        for address, name in wallet_addresses.items():
            analysis = self.wallet_analyzer.analyze_wallet(address, name)
            wallet_analyses[address.lower()] = analysis
            time.sleep(1)  # Brief pause between wallets
        
        # Find connections between wallets
        all_addresses = set(addr.lower() for addr in wallet_addresses.keys())
        connections = self._find_connections(wallet_analyses, all_addresses)
        
        # Find external addresses (not in our known set)
        external_receivers = self._find_external_addresses(wallet_analyses, all_addresses)
        
        # Calculate network statistics
        total_received = sum(w['total_usdc_received'] for w in wallet_analyses.values())
        total_sent = sum(w['total_usdc_sent'] for w in wallet_analyses.values())
        
        network_analysis = {
            'wallet_analyses': wallet_analyses,
            'total_wallets': len(wallet_addresses),
            'total_usdc_received': total_received,
            'total_usdc_sent': total_sent,
            'network_connections': connections,
            'top_external_receivers': external_receivers[:50],
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"\n{'='*80}")
        logger.info(f"NETWORK SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"Total Wallets Analyzed: {len(wallet_addresses)}")
        logger.info(f"Total USDC Received: ${total_received:,.2f}")
        logger.info(f"Total USDC Sent: ${total_sent:,.2f}")
        logger.info(f"Internal Connections: {len(connections)}")
        logger.info(f"Top External Addresses: {len(external_receivers)}")
        
        return network_analysis
    
    def _find_connections(self, wallet_analyses: Dict, known_addresses: Set) -> List[Dict]:
        """Find transactions between known wallets"""
        connections = []
        
        for addr, analysis in wallet_analyses.items():
            for tx in analysis['all_transfers']:
                from_addr = tx['from'].lower()
                to_addr = tx['to'].lower()
                
                # Check if transaction is between two known wallets
                if from_addr in known_addresses and to_addr in known_addresses:
                    connections.append({
                        'from': from_addr,
                        'to': to_addr,
                        'amount': int(tx['value']) / 1e6,
                        'timestamp': datetime.fromtimestamp(int(tx['timeStamp'])).isoformat(),
                        'hash': tx['hash']
                    })
        
        logger.info(f"Found {len(connections)} internal network transactions")
        return connections
    
    def _find_external_addresses(self, wallet_analyses: Dict, known_addresses: Set) -> List[Dict]:
        """Find top external addresses that received funds"""
        external_volumes = {}
        
        for addr, analysis in wallet_analyses.items():
            for receiver_addr, volume in analysis['top_receivers']:
                if receiver_addr not in known_addresses:
                    external_volumes[receiver_addr] = external_volumes.get(receiver_addr, 0) + volume
        
        # Sort by volume
        sorted_external = sorted(external_volumes.items(), key=lambda x: x[1], reverse=True)
        
        result = [{'address': addr, 'total_received': vol} for addr, vol in sorted_external]
        logger.info(f"Identified {len(result)} unique external receiving addresses")
        
        return result


class ReportGenerator:
    """Generates prosecutor-ready reports"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_prosecutor_report(self, network_analysis: Dict, case_name: str = "Goliath"):
        """Generate comprehensive report for prosecutors"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Executive Summary (Text)
        summary_file = self.output_dir / f"{case_name}_Executive_Summary_{timestamp}.txt"
        self._write_executive_summary(network_analysis, summary_file)
        
        # 2. Detailed Wallet Analysis (CSV)
        wallet_csv = self.output_dir / f"{case_name}_Wallet_Analysis_{timestamp}.csv"
        self._write_wallet_analysis_csv(network_analysis, wallet_csv)
        
        # 3. Top Receivers (for subpoenas) (CSV)
        receivers_csv = self.output_dir / f"{case_name}_Top_Receivers_SUBPOENA_{timestamp}.csv"
        self._write_top_receivers_csv(network_analysis, receivers_csv)
        
        # 4. Network Connections (CSV)
        connections_csv = self.output_dir / f"{case_name}_Network_Connections_{timestamp}.csv"
        self._write_connections_csv(network_analysis, connections_csv)
        
        # 5. Complete Data (JSON)
        json_file = self.output_dir / f"{case_name}_Complete_Data_{timestamp}.json"
        self._write_json_dump(network_analysis, json_file)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"REPORTS GENERATED:")
        logger.info(f"{'='*80}")
        logger.info(f"1. Executive Summary: {summary_file}")
        logger.info(f"2. Wallet Analysis: {wallet_csv}")
        logger.info(f"3. Subpoena List: {receivers_csv}")
        logger.info(f"4. Network Connections: {connections_csv}")
        logger.info(f"5. Complete Data: {json_file}")
        
        return {
            'summary': summary_file,
            'wallets': wallet_csv,
            'receivers': receivers_csv,
            'connections': connections_csv,
            'raw_data': json_file
        }
    
    def _write_executive_summary(self, analysis: Dict, filepath: Path):
        """Write executive summary text report"""
        with open(filepath, 'w') as f:
            f.write("="*80 + "\n")
            f.write("BLOCKCHAIN FORENSICS - EXECUTIVE SUMMARY\n")
            f.write("GOLIATH VENTURES INVESTIGATION\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Analysis Date: {analysis['analysis_timestamp']}\n")
            f.write(f"Wallets Analyzed: {analysis['total_wallets']}\n")
            f.write(f"Total USDC Flow: ${analysis['total_usdc_received']:,.2f} received / ${analysis['total_usdc_sent']:,.2f} sent\n\n")
            
            f.write("WALLET CLASSIFICATIONS:\n")
            f.write("-"*80 + "\n")
            for addr, wallet in analysis['wallet_analyses'].items():
                f.write(f"\n{wallet['name']} ({addr[:10]}...):\n")
                f.write(f"  Classification: {wallet['classification']}\n")
                f.write(f"  USDC Received: ${wallet['total_usdc_received']:,.2f}\n")
                f.write(f"  USDC Sent: ${wallet['total_usdc_sent']:,.2f}\n")
                f.write(f"  Transactions: {wallet['incoming_count']} in / {wallet['outgoing_count']} out\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write("TOP EXTERNAL RECEIVING ADDRESSES (SUBPOENA TARGETS)\n")
            f.write("="*80 + "\n\n")
            
            for i, receiver in enumerate(analysis['top_external_receivers'][:20], 1):
                f.write(f"{i}. {receiver['address']}\n")
                f.write(f"   Total Received: ${receiver['total_received']:,.2f} USDC\n")
                f.write(f"   ** RECOMMEND: Subpoena exchanges for KYC **\n\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write("NETWORK CONNECTIONS (Internal Transactions)\n")
            f.write("="*80 + "\n")
            f.write(f"Total internal network transactions: {len(analysis['network_connections'])}\n")
            f.write("This suggests coordinated wallet network, not independent operations.\n")
    
    def _write_wallet_analysis_csv(self, analysis: Dict, filepath: Path):
        """Write detailed wallet analysis to CSV"""
        rows = []
        for addr, wallet in analysis['wallet_analyses'].items():
            rows.append({
                'Address': addr,
                'Name': wallet['name'],
                'Classification': wallet['classification'],
                'USDC_Received': wallet['total_usdc_received'],
                'USDC_Sent': wallet['total_usdc_sent'],
                'Net_Flow': wallet['net_flow'],
                'Incoming_Txns': wallet['incoming_count'],
                'Outgoing_Txns': wallet['outgoing_count'],
                'Unique_Senders': wallet['unique_senders'],
                'Unique_Receivers': wallet['unique_receivers'],
                'First_Activity': wallet['first_activity'],
                'Last_Activity': wallet['last_activity']
            })
        
        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False)
    
    def _write_top_receivers_csv(self, analysis: Dict, filepath: Path):
        """Write top receiving addresses for subpoenas"""
        rows = []
        for i, receiver in enumerate(analysis['top_external_receivers'], 1):
            rows.append({
                'Rank': i,
                'Address': receiver['address'],
                'Total_USDC_Received': receiver['total_received'],
                'Subpoena_Priority': 'HIGH' if i <= 10 else 'MEDIUM' if i <= 30 else 'LOW',
                'Action': 'SUBPOENA EXCHANGES FOR KYC'
            })
        
        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False)
    
    def _write_connections_csv(self, analysis: Dict, filepath: Path):
        """Write network connections to CSV"""
        if analysis['network_connections']:
            df = pd.DataFrame(analysis['network_connections'])
            df.to_csv(filepath, index=False)
    
    def _write_json_dump(self, analysis: Dict, filepath: Path):
        """Write complete analysis to JSON"""
        # Remove non-serializable data
        clean_analysis = {
            'analysis_timestamp': analysis['analysis_timestamp'],
            'total_wallets': analysis['total_wallets'],
            'total_usdc_received': analysis['total_usdc_received'],
            'total_usdc_sent': analysis['total_usdc_sent'],
            'top_external_receivers': analysis['top_external_receivers'],
            'network_connections': analysis['network_connections'],
            'wallet_summary': {
                addr: {
                    'name': w['name'],
                    'classification': w['classification'],
                    'total_usdc_received': w['total_usdc_received'],
                    'total_usdc_sent': w['total_usdc_sent'],
                    'net_flow': w['net_flow'],
                    'incoming_count': w['incoming_count'],
                    'outgoing_count': w['outgoing_count']
                }
                for addr, w in analysis['wallet_analyses'].items()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(clean_analysis, f, indent=2, default=str)


def main():
    """Main execution"""
    
    print("="*80)
    print("GOLIATH VENTURES - BLOCKCHAIN FORENSIC ANALYSIS")
    print("="*80)
    print()
    print("This tool will analyze Goliath's wallet network and generate")
    print("prosecutor-ready reports for DOJ/FBI/SEC investigation.")
    print()
    
    # Get API key (optional but recommended)
    api_key = input("Enter Etherscan API Key (or press Enter for free tier): ").strip()
    if not api_key:
        api_key = None
        print("Using free tier (5 calls/sec, 100K calls/day)")
    
    # Initialize API
    api = EtherscanAPI(api_key)
    
    # Known Goliath wallets
    goliath_wallets = {
        "0xdDBae474cD6e7DA39555d71a61e9794822c57968": "Goliath Wallet 1 - Distribution",
        "0xC37A3bb2F061C002f8127ba1E25402193dce862F": "Goliath Wallet 2 - Distribution",
        "0x77696bb39917C91A0c3908D577d5e322095425cA": "Goliath Wallet 3",
        "0x808b4dA0Be6c9512E948521452227EFc619BeA52": "Goliath Wallet 4",
        "0xd24400ae8BfEBb18cA49Be86258a3C749cf46853": "Goliath Wallet 5"
    }
    
    print(f"\nAnalyzing {len(goliath_wallets)} known Goliath wallets...")
    print("This may take 10-20 minutes depending on transaction volume.")
    print()
    
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
    print(f"\nTotal API calls made: {api.call_count}")
    print(f"Reports saved to: ./reports/")
    print("\nShare these reports with DOJ/FBI/SEC prosecutors.")
    print("="*80)


if __name__ == "__main__":
    main()
