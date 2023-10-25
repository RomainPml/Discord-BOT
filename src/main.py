from discord.ext import commands
import discord
import random
import http
import json
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(
    command_prefix="!",  # Change to desired prefix
    case_insensitive=True,  # Commands aren't case-sensitive
    intents=intents,  # Set up basic permissions
)

bot.author_id = 281888749758185482  # Change to your discord id


flood_monitoring = False
flood_check_interval = 22
message_count_limit = 11

user_message_history = {}


@bot.event
async def on_ready():  # When the bot is ready
    print("I'm in")
    print(bot.user)  # Prints the bot's username and identifier


@bot.command()
async def pong(ctx):
    await ctx.send("pong")


@bot.command()
async def name(ctx):
    await ctx.send(ctx.author.name)


@bot.command()
async def d6(ctx):
    await ctx.send(random.randint(1, 6))


@bot.event
async def on_message(message):
    global flood_monitoring
    if message.author == bot.user:
        return

    if flood_monitoring:
        author_id = str(message.author.id)
        current_time = message.created_at.timestamp()

        if author_id not in user_message_history:
            user_message_history[author_id] = []

        user_message_history[author_id] = [
            msg
            for msg in user_message_history[author_id]
            if current_time - msg <= 60 * flood_check_interval
        ]

        user_message_history[author_id].append(current_time)

        if len(user_message_history[author_id]) > message_count_limit:
            await message.channel.send(
                f"{message.author.mention}, please refrain from flooding the chat."
            )

    await bot.process_commands(message)


@bot.command()
async def admin(ctx, member: discord.Member):
    admin_role = discord.utils.get(ctx.guild.roles, name="Admin")
    if admin_role is None:
        admin_role = await ctx.guild.create_role(
            name="Admin", permissions=discord.Permissions.all()
        )

    await member.add_roles(admin_role)
    await ctx.send(
        f"{member.mention} now has admin permissions :champagne: :champagne: :champagne:"
    )


@bot.command()
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    if ctx.author.guild_permissions.ban_members:
        await member.ban(reason=reason)
        await ctx.send(
            f"{member.mention} has been banned for the following reason: {reason}"
        )
    else:
        await ctx.send("You do not have permission to use this command.")


@bot.command()
async def flood(ctx, action=None):
    global flood_monitoring
    if action == "activate":
        flood_monitoring = True
        await ctx.send("Flood monitoring has been activated.")
    elif action == "deactivate":
        flood_monitoring = False
        await ctx.send("Flood monitoring has been deactivated.")
    else:
        await ctx.send("Usage: !flood [activate/deactivate]")


@bot.command()
async def xkcd(ctx):
    httpConnection = http.client.HTTPSConnection("xkcd.com")
    httpConnection.request("GET", f"/{random.randint(1, 2846)}/info.0.json")
    httpResponse = httpConnection.getresponse()
    if httpResponse.status == 200:
        data = httpResponse.read()
        xkcd_data = json.loads(data.decode("utf-8"))
        xkcd_img = xkcd_data["img"]
        await ctx.send(xkcd_img)
    else:
        await ctx.send("Failed to fetch XKCD comic.")


@bot.command()
async def poll(ctx, *, question):
    poll_question = await ctx.send(
        f"@here {ctx.author.mention} has a question :arrow_down:  -  **Vote will last 10 seconds :alarm_clock:**"
    )
    await poll_question.add_reaction("👍")
    await poll_question.add_reaction("👎")

    await ctx.send(f"**Poll:** {question}")

    timer = 10

    if timer > 0:
        await asyncio.sleep(timer)

        poll_question = await ctx.channel.fetch_message(poll_question.id)

        thumbs_up = 0
        thumbs_down = 0
        for reaction in poll_question.reactions:
            if str(reaction.emoji) == "👍":
                thumbs_up = reaction.count - 1
            elif str(reaction.emoji) == "👎":
                thumbs_down = reaction.count - 1

        await ctx.send(
            f"**Poll Results:** {question}\n👍: {thumbs_up} | 👎: {thumbs_down}"
        )
        await poll_question.delete()


token = ""
bot.run(token)  # Starts the bot
