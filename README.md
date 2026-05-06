# Blockchain Forensics Toolkit
## Cryptocurrency Investigation and Asset Tracing Tools

A comprehensive Python-based toolkit for conducting blockchain forensic analysis, transaction tracing, and asset recovery investigations on the Ethereum blockchain.

## Overview

This toolkit was developed to analyze cryptocurrency wallets and trace fund flows in financial fraud investigations. It uses the Etherscan API to retrieve transaction data and provides automated analysis, classification, and reporting capabilities.

### Key Capabilities

- **Wallet Analysis**: Comprehensive analysis of Ethereum wallet activity including all ERC-20 tokens
- **Transaction Classification**: Automatic classification of wallets (Collection, Distribution, Operational, Inactive)
- **Network Mapping**: Multi-level recursive tracing to identify fund flow networks
- **Asset Valuation**: Current balance checks across all tokens (stablecoins, ETH, ERC-20s)
- **Report Generation**: Automated generation of CSV and JSON reports for legal proceedings
- **Evidence Quality**: All findings independently verifiable via public blockchain records

## Features

### Core Analysis Tools

1. **Basic Wallet Analysis** (`goliath_forensics.py`)
   - Analyze transaction history for specified wallet addresses
   - Calculate total volumes (received/sent)
   - Classify wallet operational patterns
   - Identify network connections
   - Generate prosecutor-ready reports

2. **Recursive Fund Tracing** (`recursive_tracer.py`)
   - Multi-level transaction tracing (configurable depth)
   - Follow funds through intermediary wallets to ultimate destinations
   - Identify terminal addresses (cash-out points)
   - Filter by minimum transaction amounts
   - Prune large networks to focus on significant flows

3. **Complete Balance Checker** (`check_all_balances_improved.py`)
   - Retrieve current holdings of ALL tokens (not just USDC)
   - Calculate balances from complete transaction history
   - Support for ETH, stablecoins, and all ERC-20 tokens
   - Generate valuation reports in USD
   - Export to multiple formats (JSON, CSV)

4. **Targeted Deep Trace** (`targeted_trace.py`)
   - Flexible tool for investigating specific addresses
   - Interactive wallet selection or file-based input
   - Configurable trace depth and amount thresholds
   - Focused reporting on specific investigation targets

### Utility Scripts

5. **Simple Launcher** (`run_forensics.py`)
   - Menu-driven interface for basic operations
   - Pre-configured for common analysis scenarios
   - Minimal setup required

## Installation

### Prerequisites

- Python 3.8 or higher
- Etherscan API key (free tier available at https://etherscan.io/apis)

### Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd blockchain-forensics-toolkit
```

2. Install required packages:
```bash
pip install requests pandas --break-system-packages
```

Or use a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install requests pandas
```

3. Obtain an Etherscan API key:
   - Visit https://etherscan.io/apis
   - Create a free account
   - Generate an API key
   - Keep this key secure

## Usage

### Quick Start

The simplest way to get started is with the launcher:

```bash
python3 run_forensics.py
```

This provides a menu with two main options:
1. Basic Analysis (5 wallets, generates summary reports)
2. Recursive Trace (multi-level fund flow analysis)

### Basic Wallet Analysis

Analyze specific wallet addresses:

```bash
python3 goliath_forensics.py
```

You'll be prompted for:
- Etherscan API key
- Wallet addresses to analyze (one per line)

Generates:
- Executive summary (TXT)
- Detailed wallet analysis (CSV)
- Top receiving addresses (CSV)
- Network connections (CSV)
- Complete data export (JSON)

### Recursive Fund Tracing

Trace funds through multiple transaction levels:

```bash
python3 recursive_tracer.py
```

Configure:
- Maximum depth (1-5 hops recommended)
- Minimum transaction amount threshold
- Source wallet addresses

Outputs:
- Terminal addresses (ultimate destinations)
- Level-by-level wallet lists
- Trace summary report
- Complete network data

### Complete Balance Check

Get current holdings across all tokens:

```bash
python3 check_all_balances_improved.py
```

Options:
1. Primary wallets only (fastest)
2. Primary + Level 1 recipients
3. Custom address list

Generates:
- Complete balance data (JSON)
- Summary by wallet (CSV)
- Detailed token-by-token breakdown (CSV)
- Aggregate totals (CSV)

All reports saved to `balance_reports/` directory.

### Targeted Investigation

For focused investigation of specific addresses:

```bash
python3 targeted_trace.py
```

Input methods:
- Interactive (enter addresses manually)
- File-based (load from text file)
- CSV import (use existing analysis results)

## Output Files

### Report Structure

All analysis tools generate timestamped reports in the `reports/` or `balance_reports/` directories:

**Basic Analysis:**
- `Goliath_Executive_Summary_[timestamp].txt` - Human-readable overview
- `Goliath_Wallet_Analysis_[timestamp].csv` - Detailed wallet data
- `Goliath_Top_Receivers_SUBPOENA_[timestamp].csv` - Priority addresses
- `Goliath_Network_Connections_[timestamp].csv` - Internal transfers
- `Goliath_Complete_Data_[timestamp].json` - Raw data

**Recursive Trace:**
- `Goliath_Recursive_Terminal_Addresses_[timestamp].csv` - Ultimate destinations
- `Goliath_Recursive_Level[0-3]_Wallets_[timestamp].csv` - By-level data
- `Goliath_Recursive_Trace_Summary_[timestamp].txt` - Overview

**Balance Reports:**
- `wallet_balances_complete_[timestamp].json` - Full data
- `wallet_balances_summary_[timestamp].csv` - One row per wallet
- `wallet_balances_detailed_[timestamp].csv` - One row per token
- `wallet_balances_totals_[timestamp].csv` - Aggregated totals

### Report Formats

**CSV Files**: Easily opened in Excel, suitable for data analysis and legal exhibits

**JSON Files**: Complete raw data for technical analysis and programmatic access

**TXT Files**: Human-readable summaries for quick review

## Methodology

### Data Collection

All data is retrieved from the Ethereum blockchain via the Etherscan API:
- Transaction histories (all incoming/outgoing transfers)
- Token transfers (ERC-20 standard)
- Current balances calculated from transaction history
- Block timestamps for temporal analysis

### Classification System

Wallets are automatically classified based on transaction patterns:

- **Collection (Investor Deposits)**: More incoming than outgoing (>2:1 ratio)
- **Distribution (Ponzi Payout)**: More outgoing than incoming (>2:1 ratio)
- **Mixed (Operational)**: Balanced incoming/outgoing activity
- **Inactive**: No significant transaction activity

### Verification

All findings are independently verifiable:
- Visit https://etherscan.io
- Enter any wallet address
- View complete transaction history
- Verify amounts and timestamps

## API Limits

### Etherscan Free Tier

- Rate limit: 5 calls per second
- Daily limit: 100,000 calls
- Records per call: 1,000 (automatic pagination)

### Estimation

**Basic Analysis (5 wallets):**
- API calls: ~500
- Time: 10-20 minutes

**Recursive Trace (Depth 3):**
- API calls: ~1,000-2,000
- Time: 30-60 minutes

**Complete Balance Check (6 wallets):**
- API calls: ~200-500
- Time: 10-20 minutes

**Complete Balance Check (26 wallets):**
- API calls: ~1,000-2,000
- Time: 30-60 minutes

## Use Cases

### Financial Fraud Investigation

- Identify wallet addresses associated with fraudulent operations
- Trace fund flows from victims to perpetrators
- Locate current asset holdings for recovery
- Map money laundering networks

### Asset Recovery

- Identify wallets with current balances
- Prioritize high-value targets for seizure
- Track funds through intermediaries to exchanges
- Generate evidence for asset freeze orders

### Legal Proceedings

- Generate court-admissible evidence reports
- Provide independently verifiable transaction data
- Support criminal and civil litigation
- Document Ponzi scheme distribution patterns

### Due Diligence

- Investigate counterparty wallet addresses
- Verify transaction history claims
- Assess wallet operational patterns
- Identify risk factors

## Best Practices

### Investigation Workflow

1. **Initial Analysis**: Start with basic wallet analysis on known addresses
2. **Network Mapping**: Use recursive trace to identify connected addresses
3. **Asset Valuation**: Run complete balance check on all identified addresses
4. **Targeted Investigation**: Deep dive on specific high-value or suspicious addresses
5. **Reporting**: Compile findings into comprehensive evidence package

### Trace Depth Guidelines

- **Depth 1-2**: Personal wallets and direct transactions
- **Depth 3-4**: Intermediary wallets before major exchanges
- **Depth 5+**: Primarily exchange hot wallets (diminishing returns)

**Recommendation**: Use Depth 3 for comprehensive analysis, Depth 4 for targeted investigations

### Data Management

- Keep raw data files (JSON) for complete audit trail
- Organize reports by investigation date
- Document API key usage (track daily call limits)
- Maintain chain of custody for legal proceedings

## Limitations

### Scope

- **Blockchain**: Ethereum mainnet only
- **Tokens**: ETH and ERC-20 standard tokens
- **Data Source**: Limited to on-chain transactions (no off-chain activity)

### Attribution

- Blockchain records addresses, not identities
- Wallet ownership requires additional evidence (exchange KYC, IP logs, device access)
- Multiple parties may control single wallet
- Transactions alone do not prove intent or knowledge

### Technical

- Large wallets (10,000+ transactions) may require extended processing time
- API rate limits may extend analysis duration
- Historical data only (cannot predict future transactions)
- Cross-chain transactions not tracked

## Troubleshooting

### Common Issues

**"API key invalid" error:**
- Verify API key is correctly entered
- Check for extra spaces or characters
- Ensure key is active on Etherscan

**"Rate limit exceeded" error:**
- Script automatically handles rate limiting (5 calls/second)
- If error persists, increase RATE_LIMIT_DELAY in code
- Check daily API call limit (100,000/day)

**"No transactions found" error:**
- Verify wallet address is correct (42 characters starting with 0x)
- Check if wallet has any token transfer history
- Wallet may only have ETH transfers (use different endpoint)

**Large file processing slow:**
- Expected for wallets with thousands of transactions
- Consider increasing minimum amount threshold
- Use targeted trace instead of full recursive analysis

**Empty balance reports:**
- Verify addresses had token transactions (not just ETH)
- Check if wallet has been active recently
- Confirm API key has necessary permissions

## Security Considerations

- **API Keys**: Never commit API keys to version control
- **Data Privacy**: Wallet addresses are public, but handle associated identity data carefully
- **Legal Compliance**: Ensure investigation is authorized and complies with local laws
- **Data Storage**: Secure storage of investigation results (may contain PII if linked to individuals)

## Legal Notice

This toolkit is designed for legitimate investigative purposes including:
- Law enforcement investigations
- Court-authorized asset recovery
- Regulatory compliance
- Fraud victim representation
- Due diligence activities

Users are responsible for ensuring their use complies with applicable laws and regulations. The authors assume no liability for misuse of these tools.

## Evidence Quality

### Admissibility Factors

**Strengths:**
- Based on immutable public blockchain records
- Independently verifiable by third parties
- Cryptographically authenticated transactions
- Permanent audit trail
- Court-accepted in numerous jurisdictions

**Supporting Evidence Needed:**
- Wallet ownership attribution (exchange KYC, device forensics)
- Intent and knowledge (communications, agreements)
- Context (business purpose, relationship to parties)

## Contributing

Improvements and bug fixes welcome. Please:
- Test thoroughly before submitting
- Document any new features
- Follow existing code style
- Update README for new functionality

## License

[Specify license - MIT, Apache 2.0, etc.]

## Disclaimer

This software is provided "as is" without warranty of any kind. All blockchain data is publicly available and analysis results should be verified independently. This toolkit is designed to assist legitimate investigations and should not be used for illegal purposes.

## Support

For issues, questions, or feature requests:
- Open an issue in the repository
- Contact: [contact information]

## Acknowledgments

Built using:
- Python 3.x
- Etherscan API (https://etherscan.io)
- Pandas library for data analysis
- Public Ethereum blockchain data

## Version History

**v1.0.0** - Initial release
- Basic wallet analysis
- Recursive fund tracing
- Complete balance checking
- Multiple report formats
- Targeted investigation tools

---

**Last Updated**: March 2026
