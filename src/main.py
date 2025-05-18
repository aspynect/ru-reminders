import discord
from discord import app_commands
from discord.ext import tasks
from os import getenv
import datetime
import zoneinfo

myColor = discord.Color.from_rgb(r=255, g=0, b=255)
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
DISCORD_TOKEN = getenv("DISCORD_TOKEN", "NO TOKEN PROVIDED")
FIRST_CHANNEL_ID = int(getenv("FIRST_CHANNEL_ID", 683090734613528636))
SECOND_CHANNEL_ID = int(getenv("SECOND_CHANNEL_ID", 1220235079289409577))
ROLE_ID = int(getenv("ROLE_ID", 1220228451940962354))


class MeetingPrompt(discord.ui.Modal, title='Questionnaire Response'):
    meetingMessage = discord.ui.TextInput(label='Enter Meeting Message:')

    async def on_submit(self, interaction: discord.Interaction):
        channel = client.get_channel(SECOND_CHANNEL_ID)
        await channel.send(f"<@&{ROLE_ID}> Meeting tonight at 8:00pm!\n{self.meetingMessage}")
        await interaction.response.send_message(f"Sent meeting reminder:\n{self.meetingMessage}")

class ReminderView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = 30*60)

    @discord.ui.button(label = "No")
    async def rejectButton(self, interaction: discord.Interaction, button:discord.ui.Button):
        await interaction.response.edit_message(content = f"{interaction.user.name}: There is no meeting today.", view = None)
        
    @discord.ui.button(label = "Yes")
    async def addButton(self, interaction: discord.Interaction, button:discord.ui.Button):
        await interaction.response.send_modal(MeetingPrompt())


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(name="sync",description="sync")
async def sync(interaction: discord.Interaction):
    await tree.sync()
    await interaction.response.send_message("sunk!", ephemeral = True)
    print("Sunk!")


#@app_commands.allowed_installs(guilds=True, users=True)
#@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
#@tree.command(name="testreminders",description="test reminders")
#async def reminderTest(interaction: discord.Interaction):
#    await interaction.response.send_message(ephemeral = True, view = ReminderView())


time = datetime.time(hour=19, minute=0, tzinfo=zoneinfo.ZoneInfo("US/Central"))
@tasks.loop(time=time)
async def reminder():
    if datetime.datetime.now(zoneinfo.ZoneInfo("US/Central")).weekday() == 2:
        channel = client.get_channel(FIRST_CHANNEL_ID)
        await channel.send("Is there a meeting today?", view = ReminderView())

@client.event
async def on_ready():
    print("Ready!")
    reminder.start()

client.run(DISCORD_TOKEN)