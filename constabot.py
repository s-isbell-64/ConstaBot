import os
import random
import io
from dotenv import load_dotenv
import requests
import discord
import syllables
import base64
from playwright.async_api import async_playwright
from discord.ext import tasks

from sayings import *

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
LEO_ID = os.getenv("LEO_ID")
WA_APP_ID = os.getenv("WA_APP_ID")
DESMOS_API_KEY = os.getenv("DESMOS_API_KEY")
WEATHER_CHANNEL_NAME = "games"
BANNED_USERS = (os.getenv("GILBERT_ID"), os.getenv("BRYAN_ID"), os.getenv("ELRIK_ID"), os.getenv("WESTIN_ID"), os.getenv("SHIV_ID"))

client = discord.Client(intents=discord.Intents.all())

DESMOS_HTML = f"""<!DOCTYPE html>
    <html><head>
        <script src="https://www.desmos.com/api/v1.13/calculator.js?apiKey={DESMOS_API_KEY}"></script>
    </head>
    <body style="margin:0">
        <div id="calculator" style="width:900px;height:600px"></div>
    </body></html>"""
SCREENSHOT_JS = """
    (exprs) => new Promise((resolve) => {
        const calc = Desmos.GraphingCalculator(
            document.getElementById('calculator')
        );
        exprs.forEach((latex, i) => calc.setExpression({ id: 'e' + i, latex: latex }));
        calc.asyncScreenshot(
            { width: 900, height: 600, targetPixelRatio: 2 },
            (dataUri) => resolve(dataUri)
        );
    })"""

async def graph_command(message):
    graph_expressions = [
        e.strip() for e in message.content.lower().replace("!graph", "").split(";") if e.strip()
    ]
    if not graph_expressions:
        await message.channel.send("Please provide a mathematical expression to graph after `!graph`")
        return

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={"width": 900, "height": 600})
            await page.set_content(DESMOS_HTML, wait_until="load")
            data_uri = await page.evaluate(SCREENSHOT_JS, graph_expressions)
            await browser.close()

        png_bytes = base64.b64decode(data_uri.split(",", 1)[1])
        await message.channel.send(file=discord.File(io.BytesIO(png_bytes), filename="graph.png"))
    except Exception as e:
        print(e)
        await message.channel.send(f"Error: {e}")    

async def wa_command(message):
    wa_query = message.content.lower().replace("!wa", "").strip()
    if wa_query:
        try:
            url = f"https://api.wolframalpha.com/v2/query?"\
                f"input={wa_query}"\
                f"&appid={WA_APP_ID}"\
                f"&format=plaintext&output=json"
            response = requests.get(url)
            r = response.json()
            for pod in r["queryresult"]["pods"]:
                title = pod["title"]
                data = pod["subpods"][0]
                plaintext = data.get("plaintext")
                if plaintext:
                    await message.channel.send(f"{title}:\n{plaintext}")
                    
        except Exception as e:
            print(e)
            await message.channel.send(f"Error: {e}")
    else:
        await message.channel.send("Please provide a Wolfram|Alpha query after `!wa`")

async def mg_command(message):
    mg_query = message.content.lower().replace("!mg", "").strip()
    if mg_query:
        shop_data = requests.get("https://magicgarden.gg/platform/v1/shops").json()
        try:
            if mg_query == "weather":
                if shop_data["weather"]["current"] is None:
                    await message.channel.send("Weather: None")
                else:
                    weather_data = shop_data["weather"]["current"]["name"]
                    await message.channel.send(f"Weather: {weather_data}")

            elif mg_query == "seed":
                seed_data = shop_data["shops"]["seed"]["items"]
                seed_names = [item["name"] for item in seed_data]
                seed_stock = [item["stock"] for item in seed_data]
                seed_prices = [item["coinPrice"] for item in seed_data]
                await message.channel.send(f"Seed Shop:\n" + "\n".join([f"{name}: {stock} ({price} coins)" for name, stock, price in zip(seed_names, seed_stock, seed_prices)]))

            elif mg_query == "egg":
                egg_data = shop_data["shops"]["egg"]["items"]
                egg_names = [item["name"] for item in egg_data]
                egg_stock = [item["stock"] for item in egg_data]
                egg_prices = [item["coinPrice"] for item in egg_data]
                await message.channel.send(f"Egg Shop:\n" + "\n".join([f"{name}: {stock} ({price} coins)" for name, stock, price in zip(egg_names, egg_stock, egg_prices)]))

            elif mg_query == "tool":
                tool_data = shop_data["shops"]["tool"]["items"]
                tool_names = [item["name"] for item in tool_data]
                tool_stock = [item["stock"] for item in tool_data]
                tool_prices = [item["coinPrice"] for item in tool_data]
                await message.channel.send(f"Tool Shop:\n" + "\n".join([f"{name}: {stock} ({price} coins)" for name, stock, price in zip(tool_names, tool_stock, tool_prices)]))

            elif mg_query == "decor":
                decor_data = shop_data["shops"]["decor"]["items"]
                decor_names = [item["name"] for item in decor_data]
                decor_stock = [item["stock"] for item in decor_data]
                decor_prices = [item["coinPrice"] for item in decor_data]
                await message.channel.send(f"Decor Shop:\n" + "\n".join([f"{name}: {stock} ({price} coins)" for name, stock, price in zip(decor_names, decor_stock, decor_prices)]))

            else:
                await message.channel.send("Invalid Magic Garden query. Please use `!mg weather`, `!mg seed`, `!mg egg`, `!mg tool`, or `!mg decor`.")

        except Exception as e:
            print(e)
            await message.channel.send(f"Error: {e}")

    else:
        await message.channel.send("Please provide a Magic Garden query after `!mg`")

async def choose_command(message):
    try:
        options = message.content.lower().replace("!choose", "").strip().split(",")
        if len(options) < 2:
            raise ValueError("Not enough options provided")
        else:
            choice = random.choice([option.strip() for option in options])
            await message.channel.send(f"I choose: {choice}")
    except Exception as e:
        print(e)
        await message.channel.send(f"Error: {e}. Please use the format `!choose option1, option2, ...`.")

async def roll_command(message):
    try:
        (num, faces) = map(int, message.content.lower().replace("!roll", "").strip().split("d"))
        if num < 1 or faces < 1:
            raise ValueError("Number of dice and faces must be positive integers")
        rolls = [random.randint(1, faces) for _ in range(num)]
        await message.channel.send(f"Rolls: {rolls}\nTotal: {sum(rolls)}")
    except Exception as e:
        print(e)
        await message.channel.send(f"Error: {e}. Please use the format `!roll NdM` where N is the number of dice and M is the number of faces.")

async def help_command(message):
    help_message = (
        "Available commands:\
        `!graph <expression>` - Graphs the given mathematical expression.\
        `!wa <query>` - Queries Wolfram|Alpha for the given input.\
        `!choose option1, option2, ...` - Randomly chooses one of the provided options.\
        `!roll NdM` - Rolls N dice with M faces and returns the results.\
        `!mg <query>` - Queries the Magic Garden API for information. Valid queries are `weather`, `seed`, `egg`, `tool`, and `decor`.\
        `!help` - Displays this help message."
    )
    await message.channel.send(help_message)

command_prefixes = {
    "!graph": graph_command,
    "!wa": wa_command,
    "!mg": mg_command,
    "!choose": choose_command,
    "!roll": roll_command,
    "!help": help_command
}

async def haiku(message):
    split = message.content.lower().split()
    for i in range(len(split) - 2):
        first = split[:(i + 1)]
        if syllables.estimate(" ".join(first)) == 5:
            for j in range(i + 1, len(split) - 1):
                second = split[(i + 1):(j + 1)]
                if syllables.estimate(" ".join(second)) == 7:
                    third = split[(j + 1):]
                    if syllables.estimate(" ".join(third)) == 5:
                        haiku_text = " ".join(first) + "\n" + " ".join(second) + "\n" + " ".join(third)
                        await message.channel.send(f"Haiku detected:\n{haiku_text}")
                        return

async def react(message, trigger):
    emoji_name = reaction_triggers.get(trigger)
    if emoji_name:
        emoji = discord.utils.get(client.emojis, name=emoji_name)
        if emoji:
            await message.add_reaction(emoji)

@tasks.loop(minutes=5)
async def weather_announcements():
    if random.randint(1, 20) != 1:
        return

    channel = discord.utils.get(client.get_all_channels(), name=WEATHER_CHANNEL_NAME)
    if channel is None:
        return

    try:
        shop_data = requests.get("https://magicgarden.gg/platform/v1/shops").json()
        current_weather = shop_data["weather"]["current"]

        if current_weather is None:
            await channel.send("Wow, there's no weather outside!")
        else:
            weather_name = current_weather["name"].lower()
            await channel.send(random.choice(weather_exclamations).format(weather=weather_name))
    except Exception as e:
        print(e)

@weather_announcements.before_loop
async def before_weather_announcements():
    await client.wait_until_ready()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')   
    channel = discord.utils.get(client.get_all_channels(), name=WEATHER_CHANNEL_NAME)
    if channel is not None:
        await channel.send("Guess who's back")
    if not weather_announcements.is_running():
        weather_announcements.start()

@client.event
async def on_message(message):
    if message.author == client.user or message.author in BANNED_USERS:
        return

    content = message.content.lower()

    if message.author.id == LEO_ID:
        await react(message, "leo")

    if syllables.estimate(content) == 17:
        await haiku(message)

    for prefix, command in command_prefixes.items():
        if content.startswith(prefix):
            await command(message)
            return
    
    for trigger in reaction_triggers.keys():
        if trigger in content.split():
            await react(message, trigger)
            content = content.replace(trigger, "")

    for keyword, response in math_responses.items():
        if keyword in content.split():
            await message.channel.send(response)
            content = content.replace(keyword, "")

    if "consty" in content.split() or "constable" in content.split() or "constabot" in content.split():
        await message.channel.send(file=discord.File('absolute_honors.png'))
        content = content.replace("consty", "").replace("constable", "").replace("constabot", "")

    if "benny" in content.split() or "benjamin" in content.split() or "gulis" in content.split():
        await message.channel.send(file=discord.File('gulis_impressed.png'))
        content = content.replace("benny", "").replace("benjamin", "").replace("gulis", "")

client.run(DISCORD_TOKEN)
