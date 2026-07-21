import os
from dotenv import load_dotenv
import discord

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
print(DISCORD_TOKEN)

client = discord.Client(intents=discord.Intents.all())

custom_leo = discord.utils.get(client.emojis, name='leo1')
custom_scott = discord.utils.get(client.emojis, name='scottie')
custom_tsa = discord.utils.get(client.emojis, name='tsa')

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')    

@client.event
async def on_message(message): 

    if "leo" in message.content.lower() and message.author != client.user:
        if custom_leo:
            await message.add_reaction(custom_leo)
        await message.channel.send(custom_leo)

    elif "scott" in message.content.lower() and message.author != client.user:
        if custom_scott:
            await message.add_reaction(custom_scott)
        await message.channel.send(custom_scott)

    elif "tsa" in message.content.lower() and message.author != client.user:
        if custom_tsa:
            await message.add_reaction(custom_tsa)
        await message.channel.send(custom_tsa)

    elif "shiv" in message.content.lower() and message.author != client.user:
        await message.channel.send("@shiv")

client.run(DISCORD_TOKEN)