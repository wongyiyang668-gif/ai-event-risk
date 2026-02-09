import os
import discord
import aiohttp
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from ui.formatters import RiskEmbedFormatter

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8000")
INGESTION_CHANNEL_ID = os.getenv("INGESTION_CHANNEL_ID") # Optional specific channel for auto-ingest

class RiskBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Sync slash commands automatically
        print("Syncing slash commands...")
        await self.tree.sync()

bot = RiskBot()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

# Event listener for specific ingestion channel
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    # If message is in the ingestion channel, auto-ingest
    if str(message.channel.id) == INGESTION_CHANNEL_ID:
        async with aiohttp.ClientSession() as session:
            payload = {
                "source": "discord",
                "sender": str(message.author.id),
                "content": message.content,
                "timestamp": message.created_at.isoformat()
            }
            async with session.post(f"{API_URL}/ingest/message", json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("risk_level") == "high":
                        await message.add_reaction("🚨")
                    else:
                        await message.add_reaction("✅")

    await bot.process_commands(message)

# Slash Commands

@bot.tree.command(name="analyze", description="Immediate risk analysis of a text snippet")
@app_commands.describe(content="The text content to analyze for risks")
async def analyze(interaction: discord.Interaction, content: str):
    await interaction.response.defer()
    
    async with aiohttp.ClientSession() as session:
        # We use the existing /events endpoint which processes text
        payload = {
            "content": content,
            "source": "discord_slash",
            "timestamp": discord.utils.utcnow().isoformat()
        }
        try:
            async with session.post(f"{API_URL}/events", json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    embed = RiskEmbedFormatter.format_analysis(data)
                    await interaction.followup.send(embed=embed)
                else:
                    err_msg = f"API Error: {resp.status}"
                    await interaction.followup.send(embed=RiskEmbedFormatter.format_error(err_msg))
        except Exception as e:
            await interaction.followup.send(embed=RiskEmbedFormatter.format_error(str(e)))

@bot.tree.command(name="stats", description="Show system metrics and status")
async def stats(interaction: discord.Interaction):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_URL}/stats") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    embed = RiskEmbedFormatter.format_stats(data)
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message(f"Could not fetch stats: {resp.status}")
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}")

@bot.tree.command(name="recent", description="List recent risk events")
@app_commands.describe(limit="Number of events to fetch (max 10)")
async def recent(interaction: discord.Interaction, limit: int = 5):
    limit = min(limit, 10)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_URL}/events?limit={limit}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if not data:
                        return await interaction.response.send_message("No recent events found.")
                    
                    description = ""
                    for item in data:
                        evt = item.get("event", {})
                        description += f"• `{evt.get('id')[:8]}`: {evt.get('content')[:50]}...\n"
                    
                    embed = discord.Embed(title=f"📅 Recent {len(data)} Events", description=description, color=discord.Color.blue())
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message(f"Error: {resp.status}")
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}")

@bot.tree.command(name="review", description="Submit a human review for an event")
@app_commands.describe(event_id="The ID of the event to review", note="Your audit feedback or note")
async def review(interaction: discord.Interaction, event_id: str, note: str):
    async with aiohttp.ClientSession() as session:
        payload = {
            "reviewer": str(interaction.user),
            "note": note
        }
        try:
            async with session.post(f"{API_URL}/events/{event_id}/review", json=payload) as resp:
                if resp.status == 200:
                    await interaction.response.send_message(f"✅ Review submitted for event `{event_id}`")
                else:
                    await interaction.response.send_message(f"❌ Failed to submit review: {resp.status}")
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}")

if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_TOKEN not found in environment.")
    else:
        bot.run(TOKEN)
