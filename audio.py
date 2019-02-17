import discord
import asyncio
import youtube_dl
import os
import typing
import json
import colorsys
import discord, datetime, time
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import has_permissions 
from time import localtime, strftime
from discord.utils import get,find
import requests as rq
import random

start_time = time.time()

bot=commands.Bot(command_prefix='b.')
bot.remove_command('help')

from discord import opus
OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll',
             'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']


def load_opus_lib(opus_libs=OPUS_LIBS):
    if opus.is_loaded():
        return True

    for opus_lib in opus_libs:
            try:
                opus.load_opus(opus_lib)
                return
            except OSError:
                pass

    raise RuntimeError('Could not load an opus lib. Tried %s' %
                       (', '.join(opus_libs)))
load_opus_lib()

in_voice=[]


players = {}
songs = {}
playing = {}


async def all_false():
    for i in bot.servers:
        playing[i.id]=False


async def checking_voice(ctx):
    await asyncio.sleep(130)
    if playing[ctx.message.server.id]== False:
        try:
            pos = in_voice.index(ctx.message.server.id)
            del in_voice[pos]
            server = ctx.message.server
            voice_client = bot.voice_client_in(server)
            await voice_client.disconnect()
            await bot.say("{} left because there was no audio playing for a while".format(bot.user.name))
        except:
            pass

@bot.event
async def on_ready():
   bot.loop.create_task(all_false())
   await bot.change_presence(game=discord.Game(name='b.help'))
   print(bot.user.name)
    
@bot.command(pass_context=True)
async def join(ctx):
    channel = ctx.message.author.voice.voice_channel
    await bot.join_voice_channel(channel)
    in_voice.append(ctx.message.server.id)
    await bot.say("JOIN")

async def player_in(con):  # After function for music
    try:
        if len(songs[con.message.server.id]) == 0:  # If there is no queue make it False
            playing[con.message.server.id] = False
            bot.loop.create_task(checking_voice(con))
    except:
        pass
    try:
        if len(songs[con.message.server.id]) != 0:  # If queue is not empty
            # if audio is not playing and there is a queue
            songs[con.message.server.id][0].start()  # start it
            await bot.send_message(con.message.channel, '```Now queueed```')
            del songs[con.message.server.id][0]  # delete list afterwards
    except:
        pass


@bot.command(pass_context=True)
async def play(ctx, *,url):

    opts = {
        'default_search': 'auto',
        'quiet': True,
    }  # youtube_dl options


    if ctx.message.server.id not in in_voice: #auto join voice if not joined
        channel = ctx.message.author.voice.voice_channel
        await bot.join_voice_channel(channel)
        in_voice.append(ctx.message.server.id)

    

    if playing[ctx.message.server.id] == True: #IF THERE IS CURRENT AUDIO PLAYING QUEUE IT
        voice = bot.voice_client_in(ctx.message.server)
        song = await voice.create_ytdl_player(url, ytdl_options=opts, after=lambda: bot.loop.create_task(player_in(ctx)))
        songs[ctx.message.server.id]=[] #make a list 
        songs[ctx.message.server.id].append(song) #add song to queue
        await bot.say("```Audio {} is queued```".format(song.title))

    if playing[ctx.message.server.id] == False:
        voice = bot.voice_client_in(ctx.message.server)
        player = await voice.create_ytdl_player(url, ytdl_options=opts, after=lambda: bot.loop.create_task(player_in(ctx)))
        players[ctx.message.server.id] = player
        # play_in.append(player)
        if players[ctx.message.server.id].is_live == True:
            await bot.say("Can not play live audio yet.")
        elif players[ctx.message.server.id].is_live == False:
            player.start()
            await bot.say("```Now playing audio```")
            playing[ctx.message.server.id] = True



@bot.command(pass_context=True)
async def queue(con):
    await bot.say("```There are currently {} audios in queue```".format(len(songs)))

@bot.command(pass_context=True)
async def pause(ctx):
    id = ctx.message.server.id
    players[id].pause()
    await bot.say("PAUSE")
    
@bot.command(pass_context=True)
async def resume(ctx):
    players[ctx.message.server.id].resume()
    await bot.say("RESUME")
    
    
@bot.command(pass_context=True)
async def volume(ctx, vol:float):
    volu = float(vol)
    players[ctx.message.server.id].volume=volu
    await bot.say("VOLUME")

@bot.command(pass_context=True)
async def skip(con): #skipping songs?
    songs[con.message.server.id].skip()
    songs.skip()
    
    
@bot.command(pass_context=True)
async def stop(con):
    players[con.message.server.id].stop()
    songs.clear()
    await bot.say("STOP")
    
    
@bot.command(pass_context=True)
async def leave(ctx):
    pos=in_voice.index(ctx.message.server.id)
    del in_voice[pos]
    server=ctx.message.server
    voice_client=bot.voice_client_in(server)
    await voice_client.disconnect()
    songs.clear()
    await bot.say("DISCONNECT")
    
    
    
@bot.command(pass_context=True)
async def ping(ctx):
    await bot.say(":ping_pong: ping!! xSSS")
    print ("user has pinged")

@bot.command(pass_context=True)
async def info(ctx, user: discord.Member):
    embed = discord.Embed(title="{}'s info".format(user.name), description="Here's what I could find.", color=0xe67e22)
    embed.add_field(name="Name", value=user.name, inline=True)
    embed.add_field(name="ID", value=user.id, inline=True)
    embed.add_field(name="Status", value=user.status, inline=True)
    embed.add_field(name="Highest role", value=user.top_role)
    embed.add_field(name="Joined", value=user.joined_at)
    embed.add_field(name="Created at", value=user.created_at)
    
    embed.add_field(name="nickname", value=user.nick)
    embed.add_field(name="Bot", value=user.bot)
    embed.set_thumbnail(url=user.avatar_url)
    await bot.say(embed=embed)

@bot.command(pass_context=True)
async def serverinfo(ctx):
    embed = discord.Embed(title="{}'s info".format(ctx.message.server.name), description="Here's what I could find.", color=0x00ff00)
    embed.set_author(name="Team Ghost")
    embed.add_field(name="Created at", value=ctx.message.server.created_at, inline=True)
    embed.add_field(name="Owner", value=ctx.message.server.owner, inline=True)
    embed.add_field(name="Name", value=ctx.message.server.name, inline=True)
    embed.add_field(name="ID", value=ctx.message.server.id, inline=True)

    
    embed.add_field(name="AFK channel", value=ctx.message.server.afk_channel, inline=True)
    embed.add_field(name="Verification", value=ctx.message.server.verification_level, inline=True)
    embed.add_field(name="Region", value=ctx.message.server.region, inline=True)
    embed.add_field(name="Roles", value=len(ctx.message.server.roles), inline=True)
    embed.add_field(name="Members", value=len(ctx.message.server.members))

    embed.set_thumbnail(url=ctx.message.server.icon_url)
    await bot.say(embed=embed)    
      


 
@bot.command(pass_context=True, no_pm=True)
async def avatar(ctx, member: discord.Member):
    """User Avatar"""
    await bot.reply("{}".format(member.avatar_url))

  



@bot.command(pass_context=True)
async def clear(ctx, number):
   if ctx.message.author.server_permissions.administrator:
    mgs = [] #Empty list to put all the messages in the log
    number = int(number) #Converting the amount of messages to delete to an integer
    async for x in bot.logs_from(ctx.message.channel, limit = number):
        mgs.append(x)
    await bot.delete_messages(mgs)

@bot.command(pass_context=True)
async def botinfo(ctx):
	embed=discord.Embed(title="Bot name", description="buddy", color=0xFFFF00)
	embed.add_field(name="Creator", value="Pratyaksh and Imran")
	embed.add_field(name="Invite link", value="[Click Here!](https://discordapp.com/api/oauth2/authorize?client_id=498036721104060417&permissions=2146958839&scope=bot)")
	embed.add_field(name="Prefix", value="b.")
	await bot.say(embed=embed)


@bot.command()
async def stats():
	servers = list(bot.servers)
	current_time = time.time()
	difference = int(round(current_time - start_time))
	text = str(datetime.timedelta(seconds=difference))
	embed = discord.Embed(title="Servers:", description=f"{str(len(servers))}", color=0xFFFF)
	embed.add_field(name="Users:", value=f"{str(len(set(bot.get_all_members())))}")
	embed.add_field(name="Uptime:", value=f"{text}")
	embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/498036721104060417/594245a2458d4163fc374abf987ed211.webp?size=1024")
	await bot.say(embed=embed) 


	
@bot.command(pass_context = True)
async def mute(ctx, member: discord.Member):
     if ctx.message.author.server_permissions.administrator or ctx.message.author.id == '455500545587675156':
        role = discord.utils.get(member.server.roles, name='Muted')
        await bot.add_roles(member, role)
        embed=discord.Embed(title="User Muted!", description="**{0}** was muted by **{1}**!".format(member, ctx.message.author), color=0xff00f6)
        await bot.say(embed=embed)
     else:
        embed=discord.Embed(title="Permission Denied.", description="You don't have permission to use this command.", color=0xff00f6)
        await bot.say(embed=embed)	
	
	
	
	
        
@bot.command(pass_context=True)
async def unmute(ctx, member: discord.Member):
     if ctx.message.author.server_permissions.administrator:
        user = ctx.message.author
        role = discord.utils.get(user.server.roles, name="UnMuted")
        await bot.add_roles(user, role)
        embed=discord.Embed(title="User UnMuted!", description="**{0}** was unmuted by **{1}**!".format(member, ctx.message.author), color=0xff00f6)
        await bot.say(embed=embed)

@bot.command(pass_context=True)
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await bot.say('{0.name} joined in {0.joined_at}'.format(member))



@bot.command(pass_context=True)
async def kick(con,user:discord.Member=None):
    if con.message.author.server_permissions.kick_members == True or con.message.author.server_permissions.administrator == True:
        await bot.kick(user)
        await bot.send_message(con.message.channel,"User {} has been kicked".format(user.name))
    else:
        embed=discord.Embed(title="Permission Denied.", description="You don't have permission to use this command.", color=0xff00f6)
        await bot.say(embed=embed)


        
@bot.command(pass_context=True)
async def ban(ctx, member: discord.Member, days: int = 1):
    if ctx.message.author.server_permissions.administrator:
        await bot.ban(member, days)
    else:
        embed=discord.Embed(title="Permission Denied.", description="You don't have permission to use this command.", color=0xff00f6)
        await bot.say(embed=embed)
	
	
@bot.command(pass_context=True)
async def unban(con,user:int):
    try:
        who=await bot.get_user_info(user)
        await bot.unban(con.message.server,who)
        await bot.say("User has been unbanned")
    except:
        await bot.say("Something went wrong")
		

        

@bot.command(pass_context=True)
async def get_id(ctx):
    await bot.say("Channel id: {}".format(ctx.message.channel.id))       
    
@bot.command()
async def repeat(ctx, times : int, content='repeating...'):
    """Repeats a message multiple times."""
    for i in range(times):
        await bot.say(content) 
   
@bot.command()
async def invite():
  	"""Bot Invite"""
  	await bot.say("\U0001f44d")
  	await bot.whisper("Add me with this link {}".format(discord.utils.oauth_url(bot.user.id)))

@bot.event
async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        pages = bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
        for page in pages:
            em = discord.Embed(description=page.strip("```").replace('<', '[').replace('>', ']'),
                               color=discord.Color.blue())
            await bot.send_message(ctx.message.channel, embed=em)
    else:
        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for page in pages:
            em = discord.Embed(description=page.strip("```").replace('<', '[').replace('>', ']'),
                               color=discord.Color.blue())
            await bot.send_message(ctx.message.channel, embed=em)    
    
@bot.command()
async def guildcount():
  	"""Bot Guild Count"""
  	await bot.say("**I'm in {} Guilds!**".format(len(bot.servers)))  
    
    
    
   
@bot.command(pass_context=True)
async def guildid(ctx):
	  """Guild ID"""
	  await bot.say("`{}`".format(ctx.message.server.id))   
    
@bot.command(pass_context=True, no_pm=True)
async def guildicon(ctx):
    """Guild Icon"""
    await bot.reply("{}".format(ctx.message.server.icon_url))
    
@bot.command(pass_context=True, hidden=True)
async def setgame(ctx, *, game):
    if ctx.message.author.id not in owner:
        return
    game = game.strip()
    if game != "":
        try:
            await bot.change_presence(game=discord.Game(name=game))
        except:
            await bot.say("Failed to change game")
        else:
            await bot.say("Successfuly changed game to {}".format(game))
    else:
        await bot.send_cmd_help(ctx)    
    
    
@bot.command(pass_context=True, hidden=True)
async def setname(ctx, *, name):
    if ctx.message.author.id not in owner:
        return
    name = name.strip()
    if name != "":
        try:
            await bot.edit_profile(username=name)
        except:
            await bot.say("Failed to change name")
        else:
            await bot.say("Successfuly changed name to {}".format(name))
    else:
        await bot.send_cmd_help(ctx)
        
        


       
        

@bot.event
async def on_member_join(member):
    for channel in member.server.channels:
        if channel.name == 'welcome':
            embed = discord.Embed(title=f'Welcome {member.mention} to {member.server.name}', description='Do not forget to check rules and never try to break any one of them', color = 0x36393E)
            embed.add_field(name='__Thanks for joining__', value='**Hope you will be active here.**', inline=True)
            embed.set_thumbnail(url=member.avatar_url) 
            embed.add_field(name='__Join position__', value='{}'.format(str(member.server.member_count)), inline=True)
            embed.add_field(name='Time of joining', value=member.joined_at)
            await asyncio.sleep(0.4)
            await bot.send_message(channel, embed=embed)


@bot.event
async def on_member_remove(member):
    for channel in member.server.channels:
        if channel.name == 'welcome':
            r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
            embed = discord.Embed(title=f'{member.name} just left {member.server.name}', description='Bye bye 👋! We will miss you 😢', color = discord.Color((r << 16) + (g << 8) + b))
            embed.add_field(name='__User left__', value='**Hope you will be back soon 😕.**', inline=True)
            embed.add_field(name='Your join position was', value=member.joined_at)
            embed.set_thumbnail(url=member.avatar_url)
            await bot.send_message(channel, embed=embed)





    
    
@bot.event
async def on_reaction_add(reaction, user):
  if reaction.emoji == '🇬':
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    embed = discord.Embed(color = discord.Color((r << 16) + (g << 8) + b))
    embed.add_field(name = 'b.invite',value ='Use it to invite our bot to your server',inline = False)
    embed.add_field(name = "info", value="Show information about a user.",inline = False)
    embed.add_field(name = "serverinfo", value="Show server information.",inline = False)
    embed.add_field(name = "get_id", value="b.get_id",inline = False)
    embed.add_field(name = "guildicon", value="b.guildicon")
    embed.add_field(name = "avatar", value="b.avatar @user [show user avatar",inline = False)
    embed.add_field(name = "guildcount", value="b.guildcount",inline = False)
    embed.add_field(name = "guildid", value="b.guildid",inline = False)
    await bot.send_message(user,embed=embed)
  if reaction.emoji == '🇲':
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    embed = discord.Embed(color = discord.Color((r << 16) + (g << 8) + b))
    embed.set_author(name='Moderation Commands Help'inline = False)
    embed.set_image(url = 'https://image.ibb.co/caM2BK/help.gif'inline = False)
    embed.add_field(name = 'ban(Ban members Permission Required) ',value ='Use it like ``b.ban @user`` to ban any user',inline = False)
    embed.add_field(name = 'warn(Kick members Permission Required)',value ='Use it like ``b.warn @user <violation type>`` to warn any user',inline = False)    
    embed.add_field(name = 'kick(Kick members Permission Required)',value ='Use it like ``b.kick @user`` to kick any user',inline = False)
    embed.add_field(name = 'clear(Manage Messages Permission Required)',value ='Use it like ``b.clear <number>`` to clear any message',inline = False)
    embed.add_field(name = 'mute(Mute members Permission Required)',value ='Use it like ``b.mute @user <time>`` to mute any user',inline = False)
    embed.add_field(name = 'unmute(Mute members Permission Required) ',value ='Use it like ``b.unmute @user`` to unmute anyone',inline = False)
    embed.add_field(name = "unban", value="b.unban user.id | for example d!unban 277983178914922497",inline = False)
    await bot.send_message(user,embed=embed)
  
  if reaction.emoji == '🏵':
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    embed = discord.Embed(color = discord.Color((r << 16) + (g << 8) + b))
    embed.set_author(name='Fun Commands.')
    embed.set_image(url = 'https://image.ibb.co/caM2BK/help.gif')
    embed.add_field(name = "dice", value="50 50 chance")
    embed.add_field(name = "coinflip", value="50 50 chance of getting tails and heads.")
    await bot.send_message(user,embed=embed)
    
 
	
	
@bot.command(pass_context = True)
async def help(ctx):
    if ctx.message.author.bot:
      return
    else:
      author = ctx.message.author
      r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
      embed = discord.Embed(color = discord.Color((r << 16) + (g << 8) + b))
      embed.set_author(name='Help')
      embed.set_image(url = 'https://image.ibb.co/caM2BK/help.gif')
      embed.add_field(name = 'Having doubts? Join our server and clear your doubts. Server link:',value ='https://discord.gg/Em6GAWh',inline = False)
      embed.add_field(name = 'React with 🇲 ',value ='Explaines all the commands which are only usable by Those who has moderation permissions. Like- Manage Messages, Kick/Ban Members,etc.',inline = False)
      embed.add_field(name = 'React with 🇬 ',value ='Explaines all the commands which are usable by everyone.',inline = False)
      embed.add_field(name = 'React with 🏵 ',value ='Explaines all the commands which are usable by everyone for fun.',inline = False)
      dmmessage = await bot.send_message(author,embed=embed)
      reaction1 = '🇲'
      reaction2 = '🇬'
      reaction3 = '🏵'
      await bot.add_reaction(dmmessage, reaction1)
      await bot.add_reaction(dmmessage, reaction2)
      await bot.add_reaction(dmmessage, reaction3)
      await bot.say('📨 Check DMs For Information')	
	
	
	
	
	
	
	
	
	
	
	
	
@bot.command(pass_context=True)
async def coinflip(ctx):
    user = ctx.message.author
    side = random.randint(0, 1)
    server = ctx.message.server
    join = discord.Embed(title="devil ", description=" ", color=0x008790)
    if side == 0:
        join.add_field(name="the coin landed on:", value="Heads!", inline=False)
        join.set_footer(text='Requested by: ' + user.name)
        await bot.send_message(ctx.message.channel, embed=join)
    if side == 1:
        join.add_field(name="the coin landed on:", value="Tails!", inline=False)
        join.set_footer(text='Requested by: ' + user.name)
        await bot.send_message(ctx.message.channel, embed=join)
        
        embed = discord.Embed(title=f"User: {ctx.message.author.name} have used coinflip command", description=f"ID: {ctx.message.author.id}", color=0xff9393)

        await bot.send_message(channel, embed=embed)	



	
    
@bot.command(pass_context=True)
async def online(con):
    amt = 0
    for i in con.message.server.members:
        if i.status != discord.Status.offline:
            amt += 1
    await bot.send_message(con.message.channel, "**Currently `{}` Members Online In `{}`**".format(amt,con.message.server.name))



@bot.command(pass_context=True)
async def offline(con):
    amt = 0
    for i in con.message.server.members:
        if i.status == discord.Status.offline:
            amt += 1
    await bot.send_message(con.message.channel, "**Currently `{}` Members Offline In `{}`**".format(amt,con.message.server.name))



import random
@bot.command(pass_context=True)
async def dice( con, min1=1, max1=6):
    """GENERATES A RANDOM FROM MIN - MAX
    MIN DEFAULT = 1
    MAX DEFAULT = 6
    MIN1 = THE SMALLEST LIMIT TO GENERATE A RANDOM NUMBER
    MAX1 = THE LIMIT TO GENERATE A RANDOM NUMBER"""
    r = random.randint(min1, max1)
    await bot.send_message(con.message.channel, "**{}**".format(r))



        
@bot.command(pass_context=True)
async def embed(ctx):
    embed = discord.Embed(title="test", description="my name Pratyaksh Dandyan", color=0x00ff00)
    embed.set_footer(text="this is a footer")
    embed.set_author(name="Team Ghost")
    embed.add_field(name="This is a field", value="no it isn't", inline=True)
    await bot.say(embed=embed)
   




   
  


   
   
   
    


  




    
bot.run(os.environ['BOT_TOKEN'])
