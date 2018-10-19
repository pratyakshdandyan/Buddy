import discord
import asyncio
import youtube_dl
import os
from discord.ext import command
from discord.ext.comands import bot


bot=commands.Bot(command_prefix='!b')




@bot.event
async def on_ready():
     bot.loop.create_task(all_flase())
     await bot.change_presence(game=discord.Game(name='buddy'))
     print(bot.user.name)
     
     
@bot.command(pass_context=True)
