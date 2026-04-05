import discord
from discord.ext import commands, tasks
from discord.utils import get
import os
import gspread
from google.oauth2.service_account import Credentials  # <-- updated import
from itertools import cycle
import logging

# Configure logging to show INFO-level messages and above
logging.basicConfig(level=logging.INFO)

from dotenv import load_dotenv

load_dotenv() # will search for .env file in local folder and load variables 


print(os.environ)

# Bot & Server Configuration
# Read all sensitive values from environment variables so they are never
# hard-coded in source control.
DISCORD_BOT_AUTH_TOKEN = os.getenv("DISCORD_BOT_AUTH")
UNVERIFIED_ROLE = int(os.getenv("ROLE_UNVERIFIED"))
VERIFIED_ROLE = int(os.getenv("ROLE_VERIFIED"))
CHANNEL_MODERATION = int(os.getenv("CHANNEL_MODERATION"))
CHANNEL_GENERAL = int(os.getenv("CHANNEL_GENERAL"))
GOOGLE_SHEETS_KEY = os.getenv("GOOGLE_SHEETS_KEY")
EMAIL_ADDRESS_KEY = int(os.getenv("EMAIL_ADDRESS_KEY"))
NICKNAME_KEY = int(os.getenv("NICKNAME_KEY"))

# Google Service Account Credentials
# The private key is stored as a single-line string in the .env file with
# literal \n characters, replace them with real newlines before use.
AUTH_PROJECT_ID = os.getenv("AUTH_PROJECT_ID")
AUTH_KEY_ID = os.getenv("AUTH_KEY_ID")
AUTH_KEY = os.getenv("AUTH_PRIVATE_KEY")
AUTH_KEY = AUTH_KEY.replace('\\n', '\n')
AUTH_CLIENT_EMAIL = os.getenv("AUTH_CLIENT_EMAIL")
AUTH_CLIENT_ID = os.getenv("AUTH_CLIENT_ID")
AUTH_CERT_URL = os.getenv("AUTH_CERT_URL")

# Scopes required to read the Google Sheet and access Google Drive
scopes = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive'
]

creds_dict = {
  "type": "service_account",
  "project_id": AUTH_PROJECT_ID,
  "private_key_id": AUTH_KEY_ID,
  "private_key": AUTH_KEY,
  "client_email": AUTH_CLIENT_EMAIL,
  "client_id": AUTH_CLIENT_ID,
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": AUTH_CERT_URL,
  "universe_domain": "googleapis.com"
}

# Create Google API credentials object from the dictionary
creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)


# Initialise the Discord bot with a "!" prefix and all gateway intents enabled
client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Authenticate with Google Sheets API
file = gspread.authorize(creds)

# Open the target Google Sheets workbook by its key
workbook = file.open_by_key(GOOGLE_SHEETS_KEY)


@client.event
async def on_ready():
    logging.info("Connected")
    change_status.start()

# Cycle of artist names used for the bot's rotating status message
bot_status = cycle([
  "Joji", "Red Velvet", "Arijit Singh", "TWICE", "BLACKPINK", "NewJeans",
  "Atif Aslam", "Keshi", "BTS"
])

@tasks.loop(seconds=120)
async def change_status():
  await client.change_presence(activity=discord.Activity(
    type=discord.ActivityType.listening, name=next(bot_status)))

"""
    verify
    @params ~ 
"""
@client.command()
async def verify(ctx, w):
    try: 
        ex = False
        
        # prevent reverification of members
        with open('existingmembers.txt') as x:
            for co in x:
                co = co.rstrip()
                if w.lower() == co:
                    ex = True
                    await ctx.send("This email has already been verified!")
                    break
                else:
                    ex = False

        
        if not ex:
            # Fetch a fresh copy of the roster from Google Sheets
            # A new authorisation is created each call to avoid stale tokens.
            file = gspread.authorize(creds)
            workbook = file.open_by_key(GOOGLE_SHEETS_KEY)
            sheet = workbook.sheet1
            col = sheet.col_values(EMAIL_ADDRESS_KEY)
            namecol = sheet.col_values(NICKNAME_KEY)
            exi = False
            logging.info(f"[DEBUG] Finding: {w}")

            #Search for the provided email in the roster and verify the user if found
            for i in range(len(col)):
                if (col[i] == w):
                    member = ctx.author
                    guild = ctx.guild
                    await ctx.send("Verification Successful")
                    roler = guild.get_role(UNVERIFIED_ROLE)
                    await member.remove_roles(roler)
                    exi = True
                    ch = ctx.guild.get_channel(CHANNEL_GENERAL)
                    ch2 = ctx.guild.get_channel(CHANNEL_MODERATION)
                    role = guild.get_role(VERIFIED_ROLE)
                    await member.add_roles(role)
                    await ctx.channel.purge(limit=1)
                    await member.edit(nick=namecol[i])
                    await ch.send(f'Welcome to the AASIA Discord! {member.mention}')
                    upd = open("existingmembers.txt", "a")
                    upd.write('\n')
                    upd.write(w)
                    await ch2.send(f'{w} verified by {member}')
                    break

            #Notify the user if the email was not found
            if exi == False:
                logging.warning(f"[WARNING] Not found: {w}")
                await ctx.send("There was an error verifying your email; there was either a typo or the email is not registered with AASIA. Please contact the webmaster if you have any questions.")
    
    # Catch-all for unexpected errors
    except Exception as e:
        logging.error("Fatal Error occurred:")
        logging.error(e)

# Run the bot with the authentication token from the environment variable
client.run(DISCORD_BOT_AUTH_TOKEN)

