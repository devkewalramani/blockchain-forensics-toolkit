# Usage Guide - Blockchain Forensics Toolkit

## Quick Start Examples

### Example 1: Investigate a Single Wallet

**Scenario**: You have one wallet address and want to see its complete activity.

```bash
python3 goliath_forensics.py
```

**When prompted:**
```
Enter Etherscan API Key: [paste your key]
Enter wallet address (empty to finish): 0xddbae474cd6e7da39555d71a61e9794822c57968
Enter wallet address (empty to finish): [press Enter]
```

**Output**: Creates 5 files in `reports/` directory showing all activity, connections, and top recipients.

---

### Example 2: Check Current Balance (All Tokens)

**Scenario**: You want to know the current USD value of assets in a wallet.

```bash
python3 check_all_balances_improved.py
```

**Choose option 3** (custom), then enter:
```
Address: 0x80787af194c33b74a811f5e5c549316269d7ee1a
Name: Investigation Target
[Press Enter on empty line]
```

**Output**: Shows all tokens (USDC, USDT, ETH, etc.) and total USD value.

---

### Example 3: Trace Where Money Went

**Scenario**: Follow funds from a source wallet to see where they ended up.

```bash
python3 targeted_trace.py
```

**Configure:**
- Enter wallet address
- Max depth: 3
- Min amount: 5000

**Output**: Shows the complete path: Source → Intermediaries → Final Destinations

---

### Example 4: Analyze Multiple Related Wallets

**Scenario**: You have 5 wallet addresses that are part of the same scheme.

**Step 1**: Create a file `wallets.txt`:
```
0xddbae474cd6e7da39555d71a61e9794822c57968,Wallet 1
0xc37a3bb2f061c002f8127ba1e25402193dce862f,Wallet 2
0x77696bb39917c91a0c3908d577d5e322095425ca,Wallet 3
0x808b4da0be6c9512e948521452227efc619bea52,Wallet 4
0xd24400ae8bfebb18ca49be86258a3c749cf46853,Wallet 5
```

**Step 2**: Run recursive trace:
```bash
python3 recursive_tracer.py
```

Load the file when prompted, set depth to 3, minimum $1,000.

**Output**: Complete network map showing how all 5 wallets connect and where funds went.

---

## Common Investigation Workflows

### Workflow 1: New Investigation (Unknown Network)

**Goal**: Start with one known wallet, discover the entire network.

```bash
# Step 1: Basic analysis of known wallet
python3 goliath_forensics.py
# Enter: single wallet address

# Step 2: Review top receivers from output
# Open: reports/Goliath_Top_Receivers_SUBPOENA_*.csv

# Step 3: Trace top receivers to find network
python3 targeted_trace.py
# Enter: top 5-10 receiver addresses
# Depth: 3

# Step 4: Get current balances of entire network
python3 check_all_balances_improved.py
# Option 3: Enter all discovered addresses
```

**Result**: Complete network map with current asset values.

---

### Workflow 2: Asset Recovery Focus

**Goal**: Find where money is RIGHT NOW (current holdings).

```bash
# Step 1: Check all known addresses for current balances
python3 check_all_balances_improved.py
# Option 2: Primary + Level 1 (if you have this list)

# Step 2: Review summary
# Open: balance_reports/wallet_balances_summary_*.csv
# Sort by: Total_USD_Estimate (descending)

# Step 3: Identify top 3-5 wallets with highest balances

# Step 4: Verify on Etherscan.io
# Go to: https://etherscan.io/address/[paste address]
# Confirm balances match
```

**Result**: Prioritized list of wallets with recoverable assets.

---

### Workflow 3: Ponzi Scheme Analysis

**Goal**: Prove the scheme structure (early investors paid, later investors lost).

```bash
# Step 1: Analyze source wallets
python3 goliath_forensics.py
# Enter: suspected Ponzi wallet addresses

# Step 2: Recursive trace to find all recipients
python3 recursive_tracer.py  
# Depth: 2 (source → recipients → exchanges)
# Min: 10000 (focus on significant amounts)

# Step 3: Check current balances of ALL recipients
python3 check_all_balances_improved.py
# Load: Level 1 recipient addresses from recursive trace

# Step 4: Compare amounts
# Received from Ponzi vs Current holdings
# Early recipients: Show profit
# Later recipients: Show losses
```

**Result**: Evidence of Ponzi structure showing distribution pattern.

---

## Real-World Scenarios

### Scenario 1: "I invested $500K, where did it go?"

**Wallet**: Your investment was sent to 0xABC...123

```bash
# Trace your investment
python3 targeted_trace.py

Address: 0xABC...123
Name: My Investment Wallet
Max depth: 4
Min amount: 1000

# This shows:
# - Who else received money from that wallet
# - Where your money ultimately ended up
# - If it's still in crypto or was cashed out
```

---

### Scenario 2: "Which wallets still have money?"

**Problem**: You have 20 addresses, need to know which ones are worth pursuing.

```bash
# Fast balance check
python3 check_all_balances_improved.py

# Choose option 3 (custom)
# Paste all 20 addresses
# Review: balance_reports/wallet_balances_totals_*.csv
```

**Look for**:
- Stablecoin_Total_USD > $10,000 (easy to recover)
- ETH balance > 1.0 (worth pursuing)

---

### Scenario 3: "Prove this is a Ponzi scheme"

**Evidence needed**: Early investors got paid, later investors didn't.

```bash
# Step 1: Get all recipients
python3 recursive_tracer.py
# Source: Main wallet
# Depth: 2
# Min: 5000

# Step 2: Check their current balances
python3 check_all_balances_improved.py
# Load: Level 1 recipients from step 1

# Step 3: Create comparison
# Excel: Amount Received | Current Balance | Profit/Loss | Date
```

**Result**: 
- Early addresses (2022-2023): Received $100K, now have $150K = +$50K
- Later addresses (2024-2025): Received $100K, now have $0 = -$100K

---

## Tips & Tricks

### Tip 1: Start Small, Then Expand

Don't run recursive trace on depth 10 immediately. Try:
1. Depth 1 first (see direct recipients)
2. Review results
3. Then depth 2-3 if needed

### Tip 2: Use Appropriate Thresholds

**Minimum Amount Filtering:**
- $1,000: Comprehensive analysis
- $5,000: Focus on significant flows
- $10,000: High-value targets only
- $100,000: Major movements only

### Tip 3: Check Etherscan First

Before running analysis, visit:
```
https://etherscan.io/address/[wallet address]
```

Quick checks:
- Does it have transactions? (If 0, no point analyzing)
- Is it a contract or wallet? (Contracts are different)
- How many transactions? (Thousands = longer processing)

### Tip 4: Save API Calls

**Before running recursive trace:**
1. Check if you really need depth 4-5
2. Consider if higher minimum threshold works
3. Review Level 1 results before going deeper

**API Limit**: 100,000 calls/day
- Depth 3 trace of 5 wallets: ~1,000 calls
- Depth 5 trace: ~10,000 calls
- You can do ~10 deep traces per day

### Tip 5: Export to Excel for Analysis

All CSV files open directly in Excel. Use Excel to:
- Sort by balance (highest first)
- Filter by token type (USDC only)
- Calculate totals and percentages
- Create pivot tables

---

## Interpreting Results

### Wallet Classifications

**"Collection (Investor Deposits)"**
- Many small incoming transactions
- Few large outgoing transactions
- Likely: Collecting deposits from victims

**"Distribution (Ponzi Payout)"**
- Few large incoming transactions
- Many small outgoing transactions
- Likely: Paying out "returns" to investors

**"Mixed (Operational)"**
- Balanced incoming/outgoing
- Likely: Intermediary or exchange wallet

**"Inactive"**
- No significant activity
- May be old/abandoned wallet

### Terminal Addresses (Level 3+)

**If showing billions in volume:**
- These are exchange hot wallets (Binance, Coinbase, etc.)
- Not personal wallets
- Money went TO exchange (was cashed out)
- Need exchange KYC to identify WHO

**If showing millions:**
- Could be personal wallets
- Could be smaller exchanges
- Worth investigating further

**If showing thousands:**
- Likely personal wallets
- Good candidates for asset recovery

---

## File Organization

### Recommended Directory Structure

```
investigation/
├── scripts/                  # Toolkit scripts
│   ├── goliath_forensics.py
│   ├── recursive_tracer.py
│   └── check_all_balances_improved.py
├── data/                     # Input files
│   ├── known_wallets.txt
│   └── subjects.csv
├── reports/                  # Basic analysis output
│   └── [timestamped reports]
├── balance_reports/          # Balance check output
│   └── [timestamped reports]
└── evidence/                 # Cleaned up for court
    ├── executive_summary.pdf
    ├── wallet_balances.csv
    └── network_map.png
```

---

## Next Steps After Analysis

### For Asset Recovery

1. **Identify high-value wallets** (balance reports)
2. **Verify on Etherscan** (confirm balances)
3. **Check for exchange indicators** (billions = exchange)
4. **Prepare freeze order** (specific addresses + amounts)
5. **Submit to court** (with blockchain evidence)

### For Criminal Investigation

1. **Map complete network** (recursive trace)
2. **Identify patterns** (Ponzi distribution)
3. **Timeline analysis** (when did activity occur)
4. **Exchange KYC** (subpoena for Level 1 addresses)
5. **Connect to suspects** (match addresses to people)

### For Civil Litigation

1. **Document all wallets** (complete analysis)
2. **Calculate total flow** (amounts received/sent)
3. **Identify transfers** (specific transactions)
4. **Create exhibits** (CSV files as evidence)
5. **Expert testimony** (explain blockchain evidence)

---

## Getting Help

### If you get stuck:

1. **Check the error message** - Most errors are self-explanatory
2. **Verify API key** - 90% of issues are invalid keys
3. **Check wallet address format** - Must be 42 characters starting with 0x
4. **Review README troubleshooting section** - Common issues listed
5. **Check Etherscan directly** - Verify wallet has transactions

### Common Questions:

**Q: How long does analysis take?**
A: 10-60 minutes depending on wallet activity and depth.

**Q: Can I analyze Bitcoin wallets?**
A: No, this toolkit is Ethereum only.

**Q: Why are balances different from my analysis?**
A: You may have only tracked USDC. Use `check_all_balances_improved.py` for ALL tokens.

**Q: What if I hit API limits?**
A: Wait 24 hours for reset, or get paid API key from Etherscan.

**Q: Can I run this on 100 wallets at once?**
A: Yes, but it will take several hours. Consider batching.

---

**This guide covers 95% of common use cases. For advanced scenarios, refer to the main README or script documentation.**
