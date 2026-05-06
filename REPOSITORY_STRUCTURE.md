# Repository Structure

```
blockchain-forensics-toolkit/
│
├── README.md                           # Main documentation
├── USAGE_GUIDE.md                      # Practical examples and workflows
├── LICENSE                             # License file
├── requirements.txt                    # Python dependencies
├── .gitignore                          # Git ignore rules
│
├── core/                               # Core analysis modules
│   ├── __init__.py
│   ├── goliath_forensics.py           # Basic wallet analysis
│   └── recursive_tracer.py            # Multi-level fund tracing
│
├── tools/                              # Utility tools
│   ├── __init__.py
│   ├── check_all_balances_improved.py # Complete balance checker
│   ├── targeted_trace.py              # Focused investigation tool
│   └── run_forensics.py               # Simple launcher interface
│
├── examples/                           # Example configurations
│   ├── sample_wallets.txt             # Example wallet list format
│   ├── sample_output/                 # Example output files
│   │   ├── README.md                  # Output explanation
│   │   └── [example reports]
│   └── use_cases/                     # Documented use cases
│       ├── ponzi_investigation.md
│       ├── asset_recovery.md
│       └── network_mapping.md
│
├── docs/                               # Additional documentation
│   ├── API_REFERENCE.md               # Detailed API documentation
│   ├── METHODOLOGY.md                 # Investigation methodology
│   ├── LEGAL_CONSIDERATIONS.md        # Legal and ethical guidelines
│   └── TROUBLESHOOTING.md             # Common issues and solutions
│
└── tests/                              # Test files (optional)
    ├── test_basic_analysis.py
    └── test_recursive_trace.py
```

## File Descriptions

### Root Files

**README.md**
- Primary documentation
- Installation instructions
- Feature overview
- Quick start guide

**USAGE_GUIDE.md**
- Practical examples
- Common workflows
- Real-world scenarios
- Tips and tricks

**requirements.txt**
- Python package dependencies
- Minimal requirements for core functionality

**.gitignore**
- Excludes sensitive data (API keys, reports)
- Excludes cache and temporary files

### Core Modules (`core/`)

**goliath_forensics.py**
- Wallet transaction analysis
- Network connection identification
- Classification system
- Basic report generation

**recursive_tracer.py**
- Multi-level fund tracing
- Terminal address identification
- Network path mapping
- Advanced report generation

### Tools (`tools/`)

**check_all_balances_improved.py**
- Complete token balance calculation
- Transaction history analysis
- Multi-format reporting
- USD valuation

**targeted_trace.py**
- Flexible address selection
- Focused investigation
- Custom trace parameters
- Specialized reporting

**run_forensics.py**
- Menu-driven interface
- Pre-configured scenarios
- Simplified workflow
- Beginner-friendly

### Examples (`examples/`)

**sample_wallets.txt**
```
# Format: address,name
0x1234...abcd,Example Wallet 1
0x5678...efgh,Example Wallet 2
```

**sample_output/**
- Example CSV files
- Example JSON reports
- Example trace results
- Documentation of output format

**use_cases/**
- Documented investigation scenarios
- Step-by-step procedures
- Expected outcomes
- Interpretation guides

### Documentation (`docs/`)

**API_REFERENCE.md**
- Detailed function documentation
- Parameter specifications
- Return value formats
- Advanced usage

**METHODOLOGY.md**
- Investigation best practices
- Classification criteria
- Trace depth guidelines
- Evidence standards

**LEGAL_CONSIDERATIONS.md**
- Appropriate use cases
- Privacy considerations
- Evidence handling
- Compliance requirements

**TROUBLESHOOTING.md**
- Common error messages
- Resolution steps
- API key issues
- Performance optimization

## Setup Instructions

### For Development

1. Clone the repository:
```bash
git clone [repository-url]
cd blockchain-forensics-toolkit
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up API key:
```bash
# Option 1: Environment variable
export ETHERSCAN_API_KEY="your_key_here"

# Option 2: Enter when prompted by scripts
```

### For Users (Simple Setup)

1. Download the repository
2. Install requirements: `pip install requests pandas --break-system-packages`
3. Run launcher: `python3 tools/run_forensics.py`

## File Locations

### Input Files

Place wallet lists in repository root or `examples/` directory:
- `wallets.txt` - Your investigation targets
- `subjects.csv` - Suspect wallet addresses

### Output Files

Scripts create subdirectories automatically:
- `reports/` - Basic analysis results
- `balance_reports/` - Balance check results
- `cache/` - API response cache (gitignored)

### Evidence Files

Organize final evidence in separate directory:
```
evidence/
├── summary_report.pdf
├── wallet_analysis.csv
├── asset_locations.csv
└── blockchain_evidence.json
```

## Development Guidelines

### Adding New Tools

1. Create module in `tools/` directory
2. Follow existing code structure
3. Include docstrings and comments
4. Add usage example to `USAGE_GUIDE.md`
5. Update `README.md` features list

### Code Standards

- Python 3.8+ compatibility
- Type hints where applicable
- Comprehensive error handling
- Rate limiting respect (Etherscan)
- Clear variable naming
- Modular functions

### Documentation Standards

- Markdown format
- Clear examples
- Practical use cases
- Legal/ethical considerations
- Troubleshooting sections

## Maintenance

### Regular Updates

- Check for Etherscan API changes
- Update dependencies (`requirements.txt`)
- Add new token standards (if applicable)
- Improve classification algorithms
- Add community-requested features

### Version Control

Use semantic versioning:
- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

Example: v1.2.3

## Security

### Sensitive Data

Never commit:
- API keys
- Investigation results
- Wallet addresses under investigation
- Personal information
- Case files

### API Key Storage

Recommended approach:
```python
import os

# Try environment variable first
api_key = os.getenv('ETHERSCAN_API_KEY')

# Fall back to user input
if not api_key:
    api_key = input("Enter Etherscan API Key: ")
```

## Distribution

### For Public Release

Include:
- README.md
- USAGE_GUIDE.md
- LICENSE
- requirements.txt
- All core/ and tools/ modules
- Example files (sanitized)

Exclude:
- Actual investigation data
- API keys
- Personal configurations
- Case-specific documentation

### For Internal Use

Include everything, plus:
- Case-specific documentation
- Custom configurations
- Investigation templates
- Reporting templates

## Support

### User Support

- GitHub Issues for bugs
- Discussions for questions
- Wiki for community tips
- Email for private inquiries

### Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request
6. Update documentation

## License

[Specify your chosen license]

Common options:
- MIT: Permissive, allows commercial use
- Apache 2.0: Permissive with patent grant
- GPL v3: Copyleft, requires sharing modifications

---

This structure balances:
- Ease of use (simple scripts at top level)
- Organization (logical grouping)
- Documentation (comprehensive guides)
- Security (sensitive data excluded)
- Maintainability (clear structure)
