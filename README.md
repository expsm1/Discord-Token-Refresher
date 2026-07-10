# Discord Token Refresher

Regain control of your Discord bot if a third-party service has taken over your token.

## What It Does
- Verifies your bot token.
- Immediately regenerates the token (invalidating the old one).
- Copies the new token to your clipboard.
- Opens the Discord Developer Portal.

## Requirements
- Python 3.8+
- `customtkinter`
- `requests`

## How to Use
1. Install dependencies:
   ```bash
   pip install customtkinter requests

2. Run the script:
   ```bash
   python refresher.py
   ```
3. Paste your bot token.
4. Click "Refresh Token".
5. Copy the new token.
6. Update your `.env` file.
7. Kick any suspicious bots from your server.

<img width="898" height="204" alt="image" src="https://github.com/user-attachments/assets/8917215a-f5e9-4f6f-8604-033641926758" />

## Disclaimer
This tool is for legitimate recovery purposes only. Do not use it to steal, hijack, or take control of bots that you do not own. The author is not responsible for any misuse.

