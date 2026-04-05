# AASIA Discord Verification Bot

A Discord bot that verifies discord server members by cross-referencing their email address against a Google Sheets roster. Upon successful verification, the bot promotes the member to the Verified role, sets their server nickname and posts a welcome message.

---

## Features

- Email-based member verification via the `!verify` command
- Duplicate verification prevention using a google spreadsheet
- Automatic role assignment (removes Unverified, grants Verified tag in discord)
- Nickname auto-set from the Google Sheets roster
- Moderation channel audits the log for every successful verification
- Rotating "Listening to" bot status cycling through a list of artists (feature to make the bot more engaging)

---

## Prerequisites

- Python 3.8+
- A Discord bot token ([Discord Developer Portal](https://discord.com/developers/applications))
- A Google Cloud service account with access to the Google Sheets and Drive APIs
- A Google Sheet with at least two columns: member emails and display names (NO PII is collected)

---

## Installation

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd <repo-folder>
   ```

2. **Install dependencies**

   ```bash
   pip install discord.py gspread google-auth python-dotenv
   ```

3. **Create `existingmembers.gsheets`**

   This file tracks already-verified emails to prevent re-use.

   ```bash
   touch existingmembers.gsheets
   ```

---

## Configuration

Create a `.env` file in the project root with the following variables:

```env
# Discord
DISCORD_BOT_AUTH=your_discord_bot_token
ROLE_UNVERIFIED=123456789          # Role ID for unverified members
ROLE_VERIFIED=987654321            # Role ID for verified members
CHANNEL_MODERATION=111222333       # Channel ID for mod audit logs
CHANNEL_GENERAL=444555666          # Channel ID for welcome messages

# Google Sheets
GOOGLE_SHEETS_KEY=your_spreadsheet_id
EMAIL_ADDRESS_KEY=1                # Column number (1-based) containing emails
NICKNAME_KEY=2                     # Column number (1-based) containing display names

# Google Service Account
AUTH_PROJECT_ID=your_project_id
AUTH_KEY_ID=your_key_id
AUTH_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----
AUTH_CLIENT_EMAIL=bot@project.iam.gserviceaccount.com
AUTH_CLIENT_ID=123456789
AUTH_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/bot%40project.iam.gserviceaccount.com
```

> **Note:** The `AUTH_PRIVATE_KEY` value should be a single line with literal `\n` characters replacing actual newlines — the bot handles the conversion automatically.

---

## Google Sheets Setup

1. Create a Google Sheet with at minimum:
   - One column for registered email addresses
   - One column for member display names (nicknames)
2. Note the column numbers (1-based) and set `EMAIL_ADDRESS_KEY` and `NICKNAME_KEY` accordingly.
3. Share the sheet with your service account email (`AUTH_CLIENT_EMAIL`) as a **Viewer**.

---

## Running the Bot

```bash
python main.py
```

---

## Usage

When a new member joins the server, they receive the Unverified role tag on discord. They should run the following command in the designated verification channel:

```
!verify their.email@UIC.edu
```

**On success:**
- The Unverified role tag is removed and the Verified role is granted.
- Their discord server nickname is set to the name listed in the roster.
- The `!verify` command message is deleted from the channel.
- A welcome message is posted in the general channel.
- The verification is logged in the moderation channel.
- The email is recorded in `existingmembers.gsheets` to prevent reuse.

**On failure:**
- The member receives an error message and is advised to contact the webmaster.

---

## Project Structure

```
.
├── main.py                # Bot entry point
├── existingmembers.gsheets # Persisted list of verified emails (one per line)
├── .env                   # Environment variables (not committed to source control)
└── README.md
```

---

## Security Notes

- Never commit `.env` or any credentials file to source control. Add them to `.gitignore`.
- The service account only needs **read** access to the Google Sheet (`spreadsheets.readonly` scope).
- `existingmembers.gsheets` should be backed up periodically; losing it would allow email re-use.

