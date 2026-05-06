# Blockchain Forensics: A Structured Methodology for On-Chain Fraud Investigation

**Author:** Dev Kewalramani  
**Date:** 2025  
**Version:** 1.0

---

## Abstract

This paper presents a structured methodology for investigating alleged financial fraud using public blockchain data. The framework covers transaction flow tracing, wallet relationship mapping, fraud signature detection, and report generation suitable for legal and regulatory review. The methodology is generalized from applied investigative work and is designed to be reproducible, auditable, and defensible in legal proceedings.

---

## 1. Introduction

Public blockchain networks present a unique forensic opportunity: every transaction is permanently recorded, publicly accessible, and cryptographically verified. Unlike traditional financial fraud investigations that depend on subpoenas and bank cooperation, blockchain forensics can proceed using entirely public data sources.

This creates an asymmetry that benefits investigators. Fraudsters who use blockchain networks — often believing that pseudonymous wallet addresses provide anonymity — leave a complete, immutable record of every fund movement. The analytical challenge is not data access; it is pattern recognition across large, complex transaction graphs.

This framework provides a systematic approach to that challenge.

---

## 2. Investigation Phases

### Phase 1: Scope Definition

Before any on-chain analysis begins, the investigation scope must be defined:

- Known wallet addresses associated with the subject
- Time range of alleged fraudulent activity
- Token types and networks in scope (Ethereum mainnet, ERC-20 tokens, L2 networks)
- Legal and evidentiary requirements for the intended use of findings

Scope definition prevents scope creep and ensures that analytical effort is focused on legally relevant transactions.

### Phase 2: Seed Address Identification

The investigation begins with one or more seed addresses — wallet addresses with a confirmed link to the subject. Seed addresses are typically identified through:

- Publicly disclosed wallet addresses (social media, project websites)
- Transaction records from known counterparties (exchanges, platforms)
- On-chain patterns linking addresses to common funding sources

### Phase 3: Transaction Graph Construction

From each seed address, a transaction graph is constructed by recursively tracing inbound and outbound transactions. Graph depth is limited by the scope definition to prevent unbounded expansion.

```
Seed Address → Level 1 Neighbors → Level 2 Neighbors → ... → Terminal Nodes
```

Each node in the graph represents a unique wallet address. Each edge represents one or more transactions, weighted by total value transferred.

### Phase 4: Cluster Analysis

Related wallet addresses are identified using behavioral clustering:

**Common Funding Source Clustering**  
Wallets funded from the same source address within a short time window are likely controlled by the same party.

**Timing Pattern Clustering**  
Wallets that consistently transact within seconds of each other exhibit coordination consistent with scripted or automated control.

**Value Pattern Clustering**  
Wallets that consistently transfer identical or proportional amounts exhibit coordination consistent with fund distribution scripts.

### Phase 5: Fraud Signature Detection

Identified wallet clusters are evaluated against known fraud behavioral signatures:

**Collection (Investor Deposits)**  
High incoming transaction count with significantly fewer outgoing transactions (ratio >2:1). Signature: wallet receives from many sources, distributes to few destinations. Indicates aggregation of investor funds.

**Distribution (Ponzi Payout)**  
Low incoming transaction count with high outgoing transaction count (ratio >2:1). Signature: wallet receives from few sources, distributes to many destinations. Indicates payout distribution to investors or layering operations.

**Perfect Pass-Through**  
Near-complete redistribution of received funds (>99% of inbound value redistributed outbound). Signature: minimal capital retention, immediate redistribution. Inconsistent with legitimate investment operations which require capital retention for trading or business operations.

**Post-Suspension Activity**  
Continued wallet activity after public disclosure of fraud or payment suspension. Signature: transactions occurring after known fraud disclosure dates. Indicates ongoing operational control and potential evidence spoliation.

**Layering**  
Rapid movement of funds through multiple intermediate wallets with no economic purpose, designed to obscure the origin of funds. Signature: funds move through 3+ wallets within minutes with minimal retention at each hop.

**Structuring**  
Transactions sized to fall below reporting or detection thresholds. Signature: high volume of transactions clustered just below round number thresholds.

**Early Investor Profit Pattern**  
Recipients from scheme wallets showing net positive returns while later recipients show complete losses. Signature: early-date recipients hold more than received; late-date recipients hold near-zero balances despite large receipts. Classic Ponzi structure proof.

---

## 3. Tooling and Data Sources

### 3.1 Etherscan API

The primary data source for Ethereum network investigations. Provides:

- Transaction history by wallet address
- Token transfer history (ERC-20)
- Internal transaction traces
- Contract interaction logs

**Critical Methodology Note:** Standard API endpoints (such as `addresstokenbalance`) often miss tokens with recent activity or incomplete indexing. The methodology employed in this investigation calculates current token balances from complete transaction history rather than relying on API-reported balances. This approach:

1. Retrieves complete token transfer history via `tokentx` endpoint
2. Calculates balance as: sum(incoming transfers) - sum(outgoing transfers)
3. Captures all ERC-20 tokens including stablecoins (USDC, USDT, DAI), wrapped assets (WETH, stETH), and other tokens

This transaction-history-based approach identified $17.9M in assets versus $2.7M identified using standard balance endpoints — a 6.6x difference demonstrating the importance of comprehensive analysis methodology.

Rate limits apply to the free tier (5 calls/second, 100,000 calls/day). Paid API access is recommended for large-scale investigations.

### 3.2 Public Node Access

For investigations requiring raw transaction data or smart contract state, direct node access via providers such as Infura or Alchemy provides full EVM data access.

### 3.3 Graph Analysis

NetworkX (Python) provides the graph data structure and analysis algorithms used for wallet relationship mapping, path finding, and cluster detection.

### 3.4 Blockchain Explorers

Etherscan, Arbiscan, Polygonscan, and equivalent explorers for other EVM-compatible networks provide human-readable transaction verification and are cited as primary sources in legal reports.

---

## 4. Report Generation

### 4.1 Report Structure

Forensic reports are structured for legal review:

1. **Executive Summary** — key findings in plain language, suitable for non-technical attorneys and regulators
2. **Methodology** — description of analytical approach, data sources, and limitations
3. **Findings** — detailed transaction analysis with on-chain citations
4. **Wallet Relationship Diagram** — visual representation of the transaction graph
5. **Transaction Timeline** — chronological record of key transactions with amounts and wallet addresses
6. **Appendix** — raw transaction data supporting each finding

### 4.2 Evidentiary Standards

All findings are cited to publicly verifiable on-chain data. Every transaction referenced includes:

- Transaction hash (txHash)
- Block number and timestamp
- Sending and receiving addresses
- Value transferred
- Etherscan URL for independent verification

This structure ensures that findings can be independently verified by opposing counsel, regulators, or the court without relying on the investigator's analysis alone.

### 4.3 Limitations Disclosure

Reports explicitly disclose the limitations of on-chain analysis:

- Wallet address attribution (linking a wallet address to a specific individual) requires off-chain evidence
- On-chain analysis establishes fund flow patterns, not intent
- Privacy-preserving transactions may limit traceability at certain points in the graph

Disclosing limitations strengthens rather than weakens the report by demonstrating analytical rigor and preventing overreach claims.

---

## 5. Case Study: Ponzi Scheme Fund Flow Analysis

### 5.1 Background

This framework was applied to an investigation involving an alleged Ponzi scheme operating through a combination of traditional financial instruments and cryptocurrency. The scheme operated from February 2022 through November 2025, when investor payments ceased. The CEO was subsequently arrested on federal money laundering charges.

The on-chain component involved investor funds deposited to Ethereum wallets and subsequently moved through a series of intermediate addresses. The investigation revealed over $367 million processed through primary scheme wallets, with an additional $329 million processed through a connected collection wallet, for a total traceable flow exceeding $696 million.

Investigation was conducted using only publicly available blockchain data via the Etherscan API. All findings are independently verifiable.

### 5.2 Key Findings

**Scale and Asset Identification**  
Analysis identified $17.9 million in currently recoverable cryptocurrency assets across 26 wallet addresses. The network processed over $367 million in total transaction volume through primary wallets, with an additional $329 million processed through a connected collection wallet.

**Investor Deposit Pattern**  
Investor funds arrived at collection wallets exhibiting high incoming transaction counts (9,443 inbound transactions in the primary collection wallet) with significantly fewer outbound transactions (557), creating a 17:1 ratio consistent with aggregation behavior. Deposits followed a consistent pattern of rapid redistribution, inconsistent with legitimate investment activity.

**Network Topology**  
Transaction graph analysis identified 139 unique addresses across 4 transaction levels. Primary wallets exhibited perfect pass-through behavior with 99%+ of received funds immediately redistributed, consistent with Ponzi payment structures rather than investment operations.

**Coordinated Multi-Wallet Operations**  
Eight documented internal transfers between known scheme wallets totaling $1.5 million proved coordinated control. Transaction timing analysis showed wallet-to-wallet transfers occurring after payment suspension to investors, indicating continued operational control post-fraud disclosure.

**Early vs. Late Investor Disparity**  
Level 1 recipient analysis revealed classic Ponzi structure: two early recipient addresses received approximately $750,000 each and currently hold $3-4 million (indicating 300-400% appreciation), while thirteen later recipient addresses received $400,000-$2,000,000 each but currently hold less than $100 combined, demonstrating complete fund withdrawal.

### 5.3 Report Outcome

Findings were compiled into a structured report delivered to legal counsel for use in civil proceedings and referral to federal investigators. The blockchain analysis provided:

- **Specific Asset Recovery Targets:** 26 wallet addresses with current holdings totaling $17.9M, prioritized by value
- **Ponzi Structure Evidence:** Transaction patterns proving early investors profited while later investors lost funds
- **Post-Fraud Activity Documentation:** Wallet transactions continuing after CEO arrest, indicating ongoing conspiracy
- **Exchange Traceability:** Terminal addresses identified as major exchange hot wallets, enabling KYC subpoenas

The on-chain citations provided independent verification of all fund flow claims. Asset freeze orders were supported by specific wallet addresses and current balance documentation. All findings remain independently verifiable via public blockchain explorers.

---

## 6. Conclusion

Public blockchain networks offer investigators a complete, immutable record of financial activity. The challenge is analytical: identifying meaningful patterns across large, complex transaction graphs. This framework provides a systematic approach — from seed address identification through cluster analysis, fraud signature detection, and legally defensible report generation.

The skills required are not purely technical. Effective blockchain forensics requires understanding of both financial fraud patterns and legal evidentiary standards. The intersection of those two domains is where this methodology operates.

---

## 7. Open Source Implementation

The complete blockchain forensics toolkit implementing this methodology is available as open source software. The toolkit includes:

- Core wallet analysis modules
- Recursive transaction tracing
- Complete token balance calculation (all ERC-20 tokens)
- Automated report generation
- Network mapping and visualization data export

See github.com/devkewalramani/blockchain-forensics-toolkit for the complete implementation.

Additional projects at github.com/devkewalramani including AI governance, automated job search systems, and college football analytics.
