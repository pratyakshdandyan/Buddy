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
from discord import opus


start_time = time.time()

bot=commands.Bot(command_prefix='b.')
songs = asyncio.Queue()
play_next_song = asyncio.Event()
bot.remove_command('help')


players = {}
queues = {}

def check_queue(id):
	if queues[id] != []:
		player = queues[id].pop(0)
		players[id] = player
		player.start()






@bot.event 
async def on_ready():
	print('Logged in as')
	print("User name:", bot.user.name)
	print("User id:", bot.user.id)
	print('---------------')
    

async def audio_player_task():
    while True:
        play_next_song.clear()
        current = await songs.get()
        current.start()
        await play_next_song.wait()


def toggle_next():
    bot.loop.call_soon_threadsafe(play_next_song.set)


@bot.command(pass_context=True)
async def plays(ctx, url):
	if not client.is_voice_connected(ctx.message.server):
		voice = await client.join_voice_channel(ctx.message.author.voice_channel)
	else:
		voice = client.voice_client_in(ctx.message.server)
		
		player = await voice.create_ytdl_player(url, after=toggle_next)
		await songs.put(player)
	
	
	
	
    
@bot.command(name="join", pass_context=True, no_pm=True)
async def _join(ctx):
    user = ctx.message.author
    channel = ctx.message.author.voice.voice_channel
    await bot.join_voice_channel(channel)
    embed = discord.Embed(colour=user.colour)
    embed.add_field(name="Successfully connected to voice channel:", value=channel)
    await bot.say(embed=embed)
	
@bot.command(name="leave", pass_context=True, no_pm=True)
async def _leave(ctx):
    user = ctx.message.author
    server = ctx.message.server
    channel = ctx.message.author.voice.voice_channel
    voice_client = client.voice_client_in(server)
    await voice_client.disconnect()
    embed = discord.Embed(colour=user.colour)
    embed.add_field(name="Successfully disconnected from:", value=channel)
    await bot.say(embed=embed)

@bot.command(pass_context=True)
async def pause(ctx):
    user = ctx.message.author
    id = ctx.message.server.id
    players[id].pause()
    embed = discord.Embed(colour=user.colour)
    embed.add_field(name="Player Paused", value=f"Requested by {ctx.message.author.name}")
    await bot.say(embed=embed)

@bot.command(pass_context=True)
async def skip(ctx):
    user = ctx.message.author
    id = ctx.message.server.id
    players[id].stop()
    embed = discord.Embed(colour=user.colour)
    embed.add_field(name="Player Skipped", value=f"Requested by {ctx.message.author.name}")
    await bot.say(embed=embed)
	
@bot.command(name="play", pass_context=True)
async def _play(ctx, *, name):
	author = ctx.message.author
	name = ctx.message.content.replace("m.play ", '')
	fullcontent = ('http://www.youtube.com/results?search_query=' + name)
	text = requests.get(fullcontent).text
	soup = bs4.BeautifulSoup(text, 'html.parser')
	img = soup.find_all('img')
	div = [ d for d in soup.find_all('div') if d.has_attr('class') and 'yt-lockup-dismissable' in d['class']]
	a = [ x for x in div[0].find_all('a') if x.has_attr('title') ]
	title = (a[0]['title'])
	a0 = [ x for x in div[0].find_all('a') if x.has_attr('title') ][0]
	url = ('http://www.youtube.com'+a0['href'])
	server = ctx.message.server
	voice_client = client.voice_client_in(server)
	player = await voice_client.create_ytdl_player(url, after=lambda: check_queue(server.id))
	players[server.id] = player
	print("User: {} From Server: {} is playing {}".format(author, server, title))
	player.start()
	embed = discord.Embed(description="**__Song Play By MUZICAL DOCTORB__**")
	embed.set_thumbnail(url="https://i.pinimg.com/originals/03/2b/08/032b0870b9053a191b67dc8c3f340345.gif")
	embed.add_field(name="Now Playing", value=title)
	await bot.say(embed=embed)
	
@bot.command(pass_context=True)
async def queue(ctx, *, name):
	name = ctx.message.content.replace("m.queue ", '')
	fullcontent = ('http://www.youtube.com/results?search_query=' + name)
	text = requests.get(fullcontent).text
	soup = bs4.BeautifulSoup(text, 'html.parser')
	img = soup.find_all('img')
	div = [ d for d in soup.find_all('div') if d.has_attr('class') and 'yt-lockup-dismissable' in d['class']]
	a = [ x for x in div[0].find_all('a') if x.has_attr('title') ]
	title = (a[0]['title'])
	a0 = [ x for x in div[0].find_all('a') if x.has_attr('title') ][0]
	url = ('http://www.youtube.com'+a0['href'])
	server = ctx.message.server
	voice_client = client.voice_client_in(server)
	player = await voice_client.create_ytdl_player(url, after=lambda: check_queue(server.id))
	
	if server.id in queues:
		queues[server.id].append(player)
	else:
		queues[server.id] = [player]
	embed = discord.Embed(description="**__Song Play By MUZICAL DOCTORB__**")
	embed.add_field(name="Video queued", value=title)
	await bot.say(embed=embed)

@bot.command(pass_context=True)
async def resume(ctx):
    user = ctx.message.author
    id = ctx.message.server.id
    players[id].resume()
    embed = discord.Embed(colour=user.colour)
    embed.add_field(name="Player Resumed", value=f"Requested by {ctx.message.author.name}")
    await bot.say(embed=embed)	
	
	
	
	
	
	
	
	
	
    
    
    
@bot.command(pass_context=True)
async def ping(ctx):
    await bot.say(":ping_pong: ping!! xSSS")
    print ("user has pinged")
	
@bot.command(pass_context=True)
async def echo(*args):
	output = ''
	for word in args:
		output += word
		output += ' '
		await bot.say(output)

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
            embed = discord.Embed(title=f'Welcome {member.name} to {member.server.name}', description='Do not forget to check rules and never try to break any one of them', color = 0x36393E)
            embed.add_field(name='__Thanks for joining__', value='**Hope you will be active here.**', inline=True)
            embed.set_thumbnail(url=member.avatar_url) 
            embed.add_field(name='__Join position__', value='{}'.format(str(member.server.member_count)), inline=True)
            embed.add_field(name='Time of joining', value=member.joined_at)
            await asyncio.sleep(0.4)
            await bot.send_message(channel, embed=embed)


@bot.event
async def on_member_remove(member):
    for channel in member.server.channels:
        if channel.name == 'leave':
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
    embed.set_author(name='General Commands.')
    embed.add_field(name = 'b.invite',value ='Use it to invite our bot to your server',inline = False)
    embed.add_field(name = "info", value="Show information about a user.",inline = False)
    embed.add_field(name = "serverinfo", value="Show server information.",inline = False)
    embed.add_field(name = "get_id", value="b.get_id",inline = False)
    embed.add_field(name = "guildicon", value="b.guildicon")
    embed.add_field(name = "avatar", value="b.avatar @user [show user avatar",inline = False)
    embed.add_field(name = "guildcount", value="b.guildcount",inline = False)
    embed.add_field(name = "guildid", value="b.guildid",inline = False)
    embed.add_field(name = 'botinfo',value ='Use it like ``b.botinfo`` to get some basic info of bot',inline = False)
    embed.add_field(name = 'membercount', value='Use it like ``b.membercount`` to see how many members are in the server.', inline = False)	
    await bot.send_message(user,embed=embed)

  if reaction.emoji == '🇲':
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    embed = discord.Embed(color = discord.Color((r << 16) + (g << 8) + b))
    embed.set_author(name='Moderation Commands Help.')
    embed.set_image(url = 'https://image.ibb.co/caM2BK/help.gif')
    embed.add_field(name = 'ban(Ban members Permission Required) ',value ='Use it like ``b.ban @user`` to ban any user',inline = False)
    embed.add_field(name = 'warn(Kick members Permission Required)',value ='Use it like ``b.warn @user <violation type>`` to warn any user',inline = False)    
    embed.add_field(name = 'kick(Kick members Permission Required)',value ='Use it like ``b.kick @user`` to kick any user',inline = False)
    embed.add_field(name = 'clear(Manage Messages Permission Required)',value ='Use it like ``b.clear <number>`` to clear any message',inline = False)
    embed.add_field(name = 'mute(Mute members Permission Required)',value ='Use it like ``b.mute @user <time>`` to mute any user',inline = False)
    embed.add_field(name = 'unmute(Mute members Permission Required) ',value ='Use it like ``b.unmute @user`` to unmute anyone',inline = False)
    embed.add_field(name = "unban", value="b.unban user.id | for example b.unban 277983178914922497",inline = False)
    embed.add_field(name = 'setupwelcomer(Admin Permission required)',value ='Simply use it to make a channel named welcome so that bot will send welcome and leaves logs in that channel.',inline = False)
    embed.add_field(name = 'setuplog(Admin Permission required)',value ='Simply use it to make a channel named logs so that bot will send logs in that channel.',inline = False)
    embed.add_field(name = 'Dm(Admin Permission required)', value="Use it like ``b.dm @user <text>`` to send dm any one",inline = False)
    embed.add_field(name = 'say(Admin permission required)',value ='Use it like ``b.say <text>``',inline = False)
    embed.add_field(name = 'announce(Admin permission required)', value="Use it like ``b.announce #channel <text>``",inline = False)



    await bot.send_message(user,embed=embed)
  
  if reaction.emoji == '🏵':
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    embed = discord.Embed(color = discord.Color((r << 16) + (g << 8) + b))
    embed.set_author(name='Fun Commands.')
    embed.set_image(url = 'https://image.ibb.co/caM2BK/help.gif')
    embed.add_field(name = "dice", value="50 50 chance")
    embed.add_field(name = "coinflip", value="50 50 chance of getting tails and heads.")
    embed.add_field(name = "kiss", value="Use it like ``b.kiss @user``")
    embed.add_field(name = "hug", value="Use it like ``b.hug @user``")
    embed.add_field(name = "slap", value="Use it like ``b.slap @user``")
    embed.add_field(name = "rolldice", value="Use it like ``b.rolldice`` [fun command]")
    embed.add_field(name = "filpcoin", value="Use it like ``b.flipcoin`` [50 50 chance]")
    embed.add_field(name = 'joke',value ='Use it like ``b.joke`` to get a random joke')
    embed.add_field(name = "randomshow", value="Use it like ``b.randomshow`` [fun command]")
    embed.add_field(name = "mal", value="Use it like ``b.mal <any anime show name>`` [fun command]")
    embed.add_field(name = "img", value="Use it like ``b.img <any animel name>`` [fun command]")
    embed.add_field(name = 'Note:', value="**More commands being added soon!**")
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


@bot.event
async def on_message_delete(message):
    if not message.author.bot:
      channelname = 'logs'
      logchannel=None
      for channel in message.server.channels:
        if channel.name == channelname:
          user = message.author
      for channel in message.author.server.channels:
        if channel.name == 'logs':
          logchannel = channel
          r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
          embed = discord.Embed(color = discord.Color((r << 16) + (g << 8) + b))
          embed.set_author(name='Message deleted')
          embed.add_field(name = 'User: **{0}**'.format(user.name),value ='UserID: **{}**'.format(user.id),inline = False)
          embed.add_field(name = 'Message:',value ='{}'.format(message.content),inline = False)
          embed.add_field(name = 'Channel:',value ='{}'.format(message.channel.name),inline = False)
          await bot.send_message(logchannel,  embed=embed)


@bot.command(name="say", pass_context=True)
@commands.has_permissions(administrator=True)
async def _say(ctx, *, msg = None):
    await bot.delete_message(ctx.message)

    if not msg: await bot.say("Please specify a message to send")
    else: await bot.say(msg)
    return
    
    embed = discord.Embed(title=f"User: {ctx.message.author.name} have used say command", description=f"ID: {ctx.message.author.id}", color=0xff9393)
    await bot.send_message(channel, embed=embed)
	

@_say.error
async def say_error(error, ctx):
	if isinstance(error, discord.ext.commands.errors.CheckFailure):
		text = "Sorry {}, you do not have a administrator permission to use this command.".format(ctx.message.author.mention)
		await bot.send_message(ctx.message.channel, text)
		
		
		
@bot.command(pass_context=True, no_pm=True)
async def membercount(ctx):
	members = set(ctx.message.server.members)
	bots = filter(lambda m: m.bot, members)
	bots = set(bots)
	users = members - bots
	await bot.send_message(ctx.message.channel, embed=discord.Embed(title="Membercount", description="{} there is {} users and {} bots with a total of {} members in this server.".format(ctx.message.author.mention, len(users), len(bots), len(ctx.message.server.members)), colour=0X008CFF))
	embed = discord.Embed(title=f"User: {ctx.message.author.name} have used membercount command", description=f"ID: {ctx.message.author.id}", color=0xff9393)
	await bot.send_message(channel, embed=embed)		
		
		
		
@bot.command(pass_context=True)
async def slap(ctx, user: discord.Member = None):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    gifs = ["http://rs20.pbsrc.com/albums/b217/strangething/flurry-of-blows.gif?w=280&h=210&fit=crop", "https://media.giphy.com/media/LB1kIoSRFTC2Q/giphy.gif", "https://i.imgur.com/4MQkDKm.gif"]
    if user == None:
        await bot.say(f"{ctx.message.author.mention} ```Proper usage is\n\n>slap <mention a user>```")
    else:
        embed = discord.Embed(title=f"{ctx.message.author.name} Just slapped the shit out of {user.name}!", color = discord.Color((r << 16) + (g << 8) + b))
        embed.set_image(url=random.choice(gifs))
        await bot.say(embed=embed)	
		
		
		
@bot.command(pass_context=True)
async def kiss(ctx, user: discord.Member):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    randomurl = ["https://media3.giphy.com/media/G3va31oEEnIkM/giphy.gif", "https://i.imgur.com/eisk88U.gif", "https://media1.tenor.com/images/e4fcb11bc3f6585ecc70276cc325aa1c/tenor.gif?itemid=7386341", "http://25.media.tumblr.com/6a0377e5cab1c8695f8f115b756187a8/tumblr_msbc5kC6uD1s9g6xgo1_500.gif"]
    if user.id == ctx.message.author.id:
        await bot.say("Goodluck kissing yourself {}".format(ctx.message.author.mention))
    else:
        embed = discord.Embed(title=f"{user.name} You just got a kiss from {ctx.message.author.name}", color = discord.Color((r << 16) + (g << 8) + b))
        embed.set_image(url=random.choice(randomurl))
        await bot.say(embed=embed)



@bot.command(pass_context=True)
async def hug(ctx, user: discord.Member):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    if user.id == ctx.message.author.id:
        await bot.say("{} Wanted to hug himself/herself , good luck on that you will look like an idiot trying to do it".format(user.mention))
    else:
        randomurl = ["http://gifimage.net/wp-content/uploads/2017/09/anime-hug-gif-5.gif", "https://media1.tenor.com/images/595f89fa0ea06a5e3d7ddd00e920a5bb/tenor.gif?itemid=7919037", "https://media.giphy.com/media/NvkwNVuHdLRSw/giphy.gif"]
        embed = discord.Embed(title=f"{user.name} You just got a hug from {ctx.message.author.name}", color = discord.Color((r << 16) + (g << 8) + b))
        embed.set_image(url=random.choice(randomurl))
        await bot.say(embed=embed)
	
	
@bot.command(pass_context=True)
async def joke(ctx):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    joke = ["What do you call a frozen dog?\nA pupsicle", "What do you call a dog magician?\nA labracadabrador", "What do you call a large dog that meditates?\nAware wolf", "How did the little scottish dog feel when he saw a monster\nTerrier-fied!", "Why did the computer show up at work late?\nBecause it had a hard drive", "Autocorrect has become my worst enime", "What do you call an IPhone that isn't kidding around\nDead Siri-ous", "The guy who invented auto-correct for smartphones passed away today\nRestaurant in peace", "You know you're texting too much when you say LOL in real life, instead of laughing", "I have a question = I have 18 Questions\nI'll look into it = I've already forgotten about it", "Knock Knock!\nWho's there?\Owls say\nOwls say who?\nYes they do.", "Knock Knock!\nWho's there?\nWill\nWill who?\nWill you just open the door already?", "Knock Knock!\nWho's there?\nAlpaca\nAlpaca who?\nAlpaca the suitcase, you load up the car.", "Yo momma's teeth is so yellow, when she smiled at traffic, it slowed down.", "Yo momma's so fat, she brought a spoon to the super bowl.", "Yo momma's so fat, when she went to the beach, all the whales started singing 'We are family'", "Yo momma's so stupid, she put lipstick on her forehead to make up her mind.", "Yo momma's so fat, even Dora can't explore her.", "Yo momma's so old, her breast milk is actually powder", "Yo momma's so fat, she has to wear six different watches: one for each time zone", "Yo momma's so dumb, she went to the dentist to get a bluetooth", "Yo momma's so fat, the aliens call her 'the mothership'", "Yo momma's so ugly, she made an onion cry.", "Yo momma's so fat, the only letters she knows in the alphabet are K.F.C", "Yo momma's so ugly, she threw a boomerang and it refused to come back", "Yo momma's so fat, Donald trump used her as a wall", "Sends a cringey joke\nTypes LOL\nFace in real life : Serious AF", "I just got fired from my job at the keyboard factory. They told me I wasn't putting enough shifts.", "Thanks to autocorrect, 1 in 5 children will be getting a visit from Satan this Christmas.", "Have you ever heard about the new restaurant called karma?\nThere's no menu, You get what you deserve.", "Did you hear about the claustrophobic astronaut?\nHe just needed a little space", "Why don't scientists trust atoms?\nBecase they make up everything", "How did you drown a hipster?\nThrow him in the mainstream", "How does moses make tea?\nHe brews", "A man tells his doctor\n'DOC, HELP ME. I'm addicted to twitter!'\nThe doctor replies\n'Sorry i don't follow you...'", "I told my wife she was drawing her eyebrows too high. She looked surprised.", "I threw a boomeranga a few years ago. I now live in constant fear"]
    embed = discord.Embed(color = discord.Color((r << 16) + (g << 8) + b))
    embed.add_field(name=f"Here is a random joke that {ctx.message.author.name} requested", value=random.choice(joke))
    await bot.say(embed=embed)		
		
@bot.command(pass_context=True)
async def burned(ctx):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    embed = discord.Embed(color = discord.Color((r << 16) + (g << 8) + b))
    embed.set_image(url="https://i.imgur.com/wY4xbak.gif")
    await bot.say(embed=embed)
    await bot.delete_message(ctx.message)





@bot.command(pass_context = True)
async def dm(ctx, user: discord.Member, *, msg: str):
   if user is None or msg is None:
       await bot.say('Invalid args. Use this command like: ``d?dm @user message``')
   if ctx.message.author.server_permissions.kick_members == False:
       await bot.say('**You do not have permission to use this command**')
       return
   else:
       await bot.send_message(user, msg)
       await bot.delete_message(ctx.message)          
       await bot.say("Success! Your DM has made it! :white_check_mark: ")


@bot.command(pass_context = True)
async def flipcoin(ctx):
    choices = ['Heads', 'Tails', 'Coin self-destructed']
    color = discord.Color(value=0x00ff00)
    embed=discord.Embed(color=color, title='Flipped a coin!')
    embed.description = random.choice(choices)
    await bot.send_typing(ctx.message.channel)
    await bot.say(embed=embed)	
	
	
@bot.command(pass_context = True)
async def rolldice(ctx):
    choices = ['1', '2', '3', '4', '5', '6']
    color = discord.Color(value=0x00ff00)
    em = discord.Embed(color=color, title='Rolled! (1 6-sided die)', description=random.choice(choices))
    await bot.send_typing(ctx.message.channel)
    await bot.say(embed=em)




@bot.command(pass_context = True)
async def announce(ctx, channel: discord.Channel=None, *, msg: str=None):
    member = ctx.message.author
    if channel is None or msg is None:
        await bot.say('Invalid args. Use this command like ``d?announce #channel text here``')
        return
    else:
        if member.server_permissions.administrator == False:
            await bot.say('**You do not have permission to use this command**')
            return
        else:
            r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
            embed=discord.Embed(title="Announcement", description="{}".format(msg), color = discord.Color((r << 16) + (g << 8) + b))
            await bot.send_message(channel, embed=embed)
            await bot.delete_message(ctx.message)

	
@bot.event
async def on_message_edit(before, after):
    if before.content == after.content:
      return
    if before.author == bot.user:
      return
    else:
      user = before.author
      member = after.author
      for channel in user.server.channels:
        if channel.name == 'logs':
            r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
            embed = discord.Embed(color = discord.Color((r << 16) + (g << 8) + b))
            embed.set_author(name='Message edited')
            embed.add_field(name = 'User: **{0}**'.format(user.name),value ='UserID: **{}**'.format(user.id),inline = False)
            embed.add_field(name = 'Before:',value ='{}'.format(before.content),inline = False)
            embed.add_field(name = 'After:',value ='{}'.format(after.content),inline = False)
            embed.add_field(name = 'Channel:',value ='{}'.format(before.channel.name),inline = False)
            await bot.send_message(channel, embed=embed)
		
		
		
@bot.command(pass_context = True)
async def setupwelcomer(ctx):
    if ctx.message.author.bot:
      return
    if ctx.message.author.server_permissions.administrator == False:
      await bot.say('**You do not have permission to use this command**')
      return
    else:
      server = ctx.message.server
      everyone_perms = discord.PermissionOverwrite(send_messages=False, read_messages=True)
      everyone = discord.ChannelPermissions(target=server.default_role, overwrite=everyone_perms)
      await bot.create_channel(server, 'welcome',everyone)
      await bot.say(':white_check_mark:**Success setup**')		
		
		
@bot.command(pass_context = True)
async def setuplog(ctx):
    if ctx.message.author.bot:
      return
    if ctx.message.author.server_permissions.administrator == False:
      await bot.say('**You do not have permission to use this command**')
      return
    else:
      author = ctx.message.author
      server = ctx.message.server
      everyone_perms = discord.PermissionOverwrite(send_messages=False, read_messages=True)
      everyone = discord.ChannelPermissions(target=server.default_role, overwrite=everyone_perms)
      await bot.create_channel(server, 'logs',everyone)	
      await bot.say(':white_check_mark:**Success setup**')	
		
		

@bot.command(pass_context=True)
async def mal(ctx):
        session = rq.Session()
        """SEARCH FOR ANIME USING MyAnimeList. EX: s.mal Mushishi"""
        query = ctx.message.content[5:]
        url = 'https://api.jikan.moe/search/anime/{}/'.format(query)
        rq_url = session.get(url).text
        rq_json = json.loads(rq_url)
        anime_id = rq_json['result'][0]['mal_id']
        url2 = 'https://api.jikan.moe/anime/{}/stats/'.format(anime_id)
        rq_url2 = session.get(url2).text
        rq_json2 = json.loads(rq_url2)
        summary = rq_json2['synopsis']
        title_jp = rq_json2['title_japanese']
        title_en = rq_json2['title_english']
        anime_type = rq_json2['type']
        status = rq_json2['status']
        aired_from = rq_json2['aired']['from']
        members = rq_json2['members']
        popularity = rq_json2['popularity']
        rank = rq_json2['rank']
        duration = rq_json2['duration']
        rating = rq_json2['rating']
        premiered = rq_json2['premiered']
        favorites = rq_json2['favorites']
        scored_by = rq_json2['scored_by']
        score = rq_json2['score']
        #anime formatting output
        anime_picture = rq_json2['image_url']
        embed = discord.Embed(title="Title: {}".format(
            query), description=title_en+":"+title_jp, color=0xDEADBF)
        embed.add_field(name="Type", value=anime_type)
        embed.add_field(name="Status", value=status)
        embed.add_field(name="Members", value=members)
        embed.add_field(name="Popularity", value=popularity)
        embed.add_field(name="Rank", value=rank)
        embed.add_field(name="Favorites", value=favorites)
        embed.add_field(name="Score", value=score)
        embed.add_field(name="Scored By", value=scored_by)
        embed.add_field(name="Aired From", value=aired_from)
        embed.add_field(name="Rating", value=rating)
        embed.add_field(name="Duration", value=duration)
        embed.add_field(name="Premiered", value=premiered)
        embed.set_thumbnail(url=anime_picture)
        await bot.say(embed=embed)
        await bot.say("**Summary**: {}".format(summary))
	
	
	
@bot.command(pass_context=True)
async def randomshow(ctx):
    url = 'https://tv-v2.api-fetch.website/random/show'
    r = rq.get(url).text
    r_json = json.loads(r)
    name = r_json['title']
    year = r_json['year']
    img = r_json['images']['poster']
    await bot.say("**Name**: {}\n**Year**: {}\n**Poster**: {}".format(name, year, img))	
	
		
@bot.command(pass_context=True)
async def img(ctx):
    """FAILED IMAGE GENERATOR BY KEYWORDS s.img dog"""
    img_api = '142cd7a6-ce58-4647-a81d-8b82f9668b75'
    
    query = ctx.message.content[5:]
    url = 'http://version1.api.memegenerator.net//Generators_Search?q={}&apiKey={}'.format(
        query, img_api)
    rq_link = rq.get(url).text
    rq_json = json.loads(rq_link)
    await bot.say(rq_json['result'][0]['imageUrl'])



        
@bot.command(pass_context=True)
async def embed(ctx):
    embed = discord.Embed(title="test", description="my name Pratyaksh Dandyan", color=0x00ff00)
    embed.set_footer(text="this is a footer")
    embed.set_author(name="Team Ghost")
    embed.add_field(name="This is a field", value="no it isn't", inline=True)
    await bot.say(embed=embed)
   




   
  


   
   
   
    


  




    
bot.run(os.environ['BOT_TOKEN'])
