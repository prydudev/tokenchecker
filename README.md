# Token Checker

A fast and efficient token checker. This tool checks and sorts tokens for validity, email verification, phone verification, and Nitro subscription status.

![Token Checker](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

[![Deploy](https://raw.githubusercontent.com/prydudev/deploy-buttons/refs/heads/main/buttons/remade/replit.svg)](https://replit.com/github/prydudev/tokenchecker)

## Installation

1. Make sure you have Python 3.8 or higher installed
2. Clone or download this repository
```bash
git clone https://github.com/prydudev/tokenchecker.git
```
3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your tokens in `tokens.txt` (one token per line)
2. Run the script:
```bash
python main.py
```

3. Use the menu to:
   - Start checking tokens
   - Manage your tokens
   - Configure settings

## Notes

- The program uses a rate limit of 10 tokens per second
- Tokens are automatically retried if rate limited
- All output files are sorted alphabetically
- Invalid tokens are filtered based on length and format

## License

- This project is licensed under the MIT License.
- This tool is for educational purposes only. 