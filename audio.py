import discord
import asyncio
import youtube_dl
import os
import typing
import json
import colorsys
import translate
import requests, bs4
import discord, datetime, time
from translate import Translator
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



async def status_task():
    while True:
        await bot.change_presence(game=discord.Game(name='b.help', type=2))
        await asyncio.sleep(5)
        await bot.change_presence(game=discord.Game(name=str(len(set(bot.get_all_members())))+' users', type=3))
        await asyncio.sleep(5)
        await bot.change_presence(game=discord.Game(name=str(len(bot.servers))+' servers', type=3))
        await asyncio.sleep(5)
        await bot.change_presence(game=discord.Game(name='music'))
        await asyncio.sleep(5)
        await bot.change_presence(game=discord.Game(name='I need some upvotes to grow ;('))
        await asyncio.sleep(5)


@bot.event 
async def on_ready():
	bot.loop.create_task(status_task())
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
	if not bot.is_voice_connected(ctx.message.server):
		voice = await bot.join_voice_channel(ctx.message.author.voice_channel)
	else:
		voice = bot.voice_client_in(ctx.message.server)
		
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
    voice_bot = bot.voice_client_in(server)
    await voice_bot.disconnect()
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
	name = ctx.message.content.replace("b.play ", '')
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
	voice_bot = bot.voice_client_in(server)
	player = await voice_bot.create_ytdl_player(url, after=lambda: check_queue(server.id))
	players[server.id] = player
	print("User: {} From Server: {} is playing {}".format(author, server, title))
	player.start()
	embed = discord.Embed(description="**__Song Play By BUDDY__**")
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
	voice_bot = bot.voice_client_in(server)
	player = await voice_bot.create_ytdl_player(url, after=lambda: check_queue(server.id))
	
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
      


@bot.command(pass_context = True)
async def avatar(ctx, user: discord.Member=None):
    if user is None:
        r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
        embed = discord.Embed(title=f'Avatar', description='Avatar is profile picture of a user in discord', color = discord.Color((r << 16) + (g << 8) + b))
        embed.add_field(name='User: {}'.format(ctx.message.author.name), value='Avatar:', inline=True)
        embed.set_thumbnail(url='https://cdn.discordapp.com/avatars/482828147155402752/7a8a3345b2eb827587710568eb1655a8.webp?size=1024') 
        embed.set_image(url = ctx.message.author.avatar_url)
        await bot.say(embed=embed)
    else:
        r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
        embed = discord.Embed(title=f'Avatar', description='Avatar is profile picture of a user in discord', color = discord.Color((r << 16) + (g << 8) + b))
        embed.add_field(name='User: {}'.format(user.name), value='Avatar:', inline=True)
        embed.set_thumbnail(url='https://cdn.discordapp.com/avatars/482828147155402752/7a8a3345b2eb827587710568eb1655a8.webp?size=1024') 
        embed.set_image(url = user.avatar_url)
        await bot.say(embed=embed)	

  



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
        
        


       
        

@bot.event
async def on_member_join(member):
    for channel in member.server.channels:
        if channel.name == 'welcome':
            r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
            embed = discord.Embed(title=f'Welcome {member.name} to {member.server.name}', description='Do not forget to check rules and never try to break any one of them', color = discord.Color((r << 16) + (g << 8) + b))
            embed.add_field(name='__Thanks for joining__', value='**Hope you will be active here.**', inline=True)
            embed.set_thumbnail(url='https://media.giphy.com/media/OkJat1YNdoD3W/giphy.gif') 
            embed.set_image(url = member.avatar_url)
            embed.add_field(name='__Join position__', value='{}'.format(str(member.server.member_count)), inline=True)
            embed.add_field(name='Time of joining', value=member.joined_at)
            await bot.send_message(channel, embed=embed)
            r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
            embed = discord.Embed(color = discord.Color((r << 16) + (g << 8) + b))
            embed.set_author(name='Welcome message')
            embed.add_field(name = '__Welcome to Our Server__',value ='**Hope you will be active here. Check Our server rules and never try to break any rules. ',inline = False)
            embed.set_image(url = 'https://media.giphy.com/media/OkJat1YNdoD3W/giphy.gif')
            await bot.send_message(member,embed=embed)
            print("Sent message to " + member.name)
            channel = discord.utils.get(client.get_all_channels(), server__name='Buddy®', name='buddy-servers-join-leave-log')
            r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
            embed = discord.Embed(title=f'Welcome {member.name} to {member.server.name}', description='Do not forget to check <#477161841487773706> and never try to break any one of them', color = discord.Color((r << 16) + (g << 8) + b))
            embed.add_field(name='__Thanks for joining__', value='**Hope you will be active here.**', inline=True)
            embed.add_field(name='Your join position is', value=member.joined_at)
            embed.set_image(url = 'https://media.giphy.com/media/OkJat1YNdoD3W/giphy.gif')
            embed.set_thumbnail(url=member.avatar_url)
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

		
@bot.command(pass_context = True)
async def help(ctx):
    server = ctx.message.server
    author = ctx.message.author
    embed = discord.Embed(title=None, description="**Help command for Buddy**", color=0xff00f6)		
    embed.add_field(name="__Moderations Commands:__", value="```\nkick :: [>kick @user reason]\nban :: [>ban @user reason]\nmute :: [>mute @user reason]\nunmute :: [>unmute @user reason]\nwarn :: [>warn @user reason]\nclear :: [ex= >clear 10]\nsay :: [>say <your msg>]\ndm :: [>dm @user msg]\nunban :: [>unban userID]\nsetupwelcomer :: [>setupwelcomer]\nsetuplog :: [>setuplog]\nannounce :: [>announce #channel <your msg>]\nembed :: [>embed <your msg>]```",inline = False)
    embed.add_field(name="__Action Commands:__", value="```\npoke :: [b.poke @user]\nkiss :: [b.kiss @user]\nslap :: [b.slap @user]\nhug :: [b.hug @user]\nbite :: [b.bite @user]\npat :: [b.pat @user]\nbloodsuck :: [b.bloodsuck @user]\ncuddle :: [b.cuddle @user]\nthuglife :: [b.thuglife]\nburned :: [b.burned]\nsavage :: [b.savage]\nfacedesk :: [b.facedesk]\nhighfive :: [b.highfive @user]```",inline = False)		      
    embed.add_field(name="__General Commands:__", value="```\nping\ninfo\nserverinfo\nmembercount\ngulidicon\nguildcount\nonline\noffline\nstats\njoined\nbotinfo```",inline = False) 		
    embed.add_field(name="__Fun Commands:__", value="```\nmeme\njoke\nmovie :: [b.movie <any movie name>]\nmal :: [b.mal <your anime show>]\ntweet :: [b.tweet <user name> <your tweet>]\nhappybirthday :: [b.happybirthday @user]\nflipcoin\nrolldice\ncoinflip\ndice```",inline = False)	
    embed.add_field(name="__Image Commands:__", value="```\nmeme\ndog\nfox\ncat\nimg\nrandomshow\nneko\nbuddy```",inline = False)	
    embed.add_field(name="__Misc Commands:__", value="```\ntweet :: [b.tweet <user.name> <your tweet>]\ntrans :: [ex = b.trans english->hindi <msg>]\neightball :: [b.eigthball <your Q>]```",inline = False)
    embed.add_field(name="__Credits__", value="**Credits to the following:**",inline = False)
    embed.add_field(name="__Head CEO of Buddy. Main Bot Developer.__", value="`Pratyaksh Dandyan#9700`",inline = False)
    embed.add_field(name="__Main Bot Helper__", value="`☠The Invisible Imran☠#4615`",inline = False)
    embed.add_field(name='Need more help?', value="Join our support server at https://discord.gg/Em6GAWh")
    embed.set_thumbnail(url=server.icon_url)
    embed.set_footer(text="Requested by: " + author.name)
    await bot.say(embed=embed)			
		
		
@bot.command(pass_context=True)
async def pat(ctx, user: discord.Member = None):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    if user == None:
        await bot.say(f"{ctx.message.author.mention} ```Proper usage is\n\n>pat <mention a user>```")
    else:
        randomurl = ["https://thumbs.gfycat.com/ImpurePleasantArthropods-small.gif", "https://i.imgur.com/4ssddEQ.gif", "https://thumbs.gfycat.com/ShockingFaroffJavalina-size_restricted.gif", "http://i.imgur.com/laEy6LU.gif", "https://i.imgur.com/NNOz81F.gif"]
        embed = discord.Embed(title=f"{user.name} You just got a patted from {ctx.message.author.name}", color = discord.Color((r << 16) + (g << 8) + b))
        embed.set_image(url=random.choice(randomurl))
        await bot.say(embed=embed)		
	
	
@bot.command(pass_context=True)
async def bite(ctx, user: discord.Member = None):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    if user == None:
        await bot.say(f"{ctx.message.author.mention} ```Proper usage is\n\n>bite <mention a user>```")
    else:
        randomurl = ["https://media.giphy.com/media/fhkRUj3BWmMnu/giphy.gif", "https://gifimage.net/wp-content/uploads/2017/09/anime-bite-gif-7.gif", "https://toxicmuffin.files.wordpress.com/2013/04/tumblr_mkzqyghtsm1r0rp7xo1_400.gif", "https://78.media.tumblr.com/tumblr_m5vv15KoxB1qklrzno2_500.gif", "https://media1.tenor.com/images/06f88667b86a701b1613bbf5fb9205e9/tenor.gif"]
        embed = discord.Embed(title=f"{user.name} you have been bitten by {ctx.message.author.name}", color = discord.Color((r << 16) + (g << 8) + b))
        embed.set_image(url=random.choice(randomurl))
        await bot.say(embed=embed)	
	
@bot.command(pass_context=True)
async def poke(ctx, user: discord.Member = None):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    if user == None:
        await bot.say(f"{ctx.message.author.mention} ```Proper usage is\n\n>poke <mention a user>```")
    else:
        randomurl = ["https://media.giphy.com/media/WvVzZ9mCyMjsc/giphy.gif", "https://gifimage.net/wp-content/uploads/2017/09/anime-poke-gif-11.gif", "https://media1.tenor.com/images/1a64ac660387543c5b779ba1d7da2c9e/tenor.gif", "https://i.gifer.com/bun.gif", "https://thumbs.gfycat.com/KeyImaginativeBushsqueaker-size_restricted.gif"]
        embed = discord.Embed(title=f"{user.name} you have been poked by {ctx.message.author.name}", color = discord.Color((r << 16) + (g << 8) + b))
        embed.set_image(url=random.choice(randomurl))
        await bot.say(embed=embed)	
	
@bot.command(pass_context=True)
async def bloodsuck(ctx, user: discord.Member = None):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    if user == None:
        await bot.say(f"{ctx.message.author.mention} ```Proper usage is\n\n>bloodsuck <mention a user>```")
    else:
        randomurl = ["https://78.media.tumblr.com/tumblr_m5vv15KoxB1qklrzno2_500.gif", "https://i1.wp.com/24.media.tumblr.com/tumblr_mcj6b5gsSr1riv2oqo1_500.gif", "https://i.imgur.com/UbaeYIq.gif", "https://i.imgur.com/CtwmzpG.gif", "https://images.gr-assets.com/hostedimages/1438121044ra/15667005.gif"]
        embed = discord.Embed(title=f"{user.name} is sucking the blood of {ctx.message.author.name}", color = discord.Color((r << 16) + (g << 8) + b))
        embed.set_image(url=random.choice(randomurl))
        await bot.say(embed=embed)	

	
@bot.command(pass_context=True)
async def cuddle(ctx, user: discord.Member = None):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    if user == None:
        await bot.say(f"{ctx.message.author.mention} ```Proper usage is\n\n>cuddle <mention a user>```")
    else:
        randomurl = ["https://media.giphy.com/media/143v0Z4767T15e/giphy.gif", "https://i.imgur.com/nrdYNtL.gif", "https://media1.tenor.com/images/8f8ba3baeecdf28f3e0fa7d4ce1a8586/tenor.gif", "https://66.media.tumblr.com/18fdf4adcb5ad89f5469a91e860f80ba/tumblr_oltayyHynP1sy5k7wo1_400.gif", "https://i.imgur.com/wOmoeF8.gif"]
        embed = discord.Embed(title=f"{user.name} you have been cuddled by {ctx.message.author.name}", color = discord.Color((r << 16) + (g << 8) + b))
        embed.set_image(url=random.choice(randomurl))
        await bot.say(embed=embed)	
	
@bot.command(pass_context=True)
async def highfive(ctx, user: discord.Member = None):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    if user == None:
        await bot.say(f"{ctx.message.author.mention} ```Proper usage is\n\n>highfive <mention a user>```")
    else:
        randomurl = ["http://rs584.pbsrc.com/albums/ss289/vampgirl17/Danny%20Phantom/hifive.gif", "https://thumbs.gfycat.com/ActualWarmheartedDungbeetle-small.gif", "https://media1.tenor.com/images/aed08ae3d802b0de9791057e2dadf7a6/tenor.gif", "https://i.pinimg.com/originals/d2/b2/7c/d2b27cdf7a0d320e18efbe21dfca9a50.gif", "https://media1.tenor.com/images/9730876547cb3939388cf79b8a641da9/tenor.gif"]
        embed = discord.Embed(title=f"{user.name} highfives {ctx.message.author.name}", color = discord.Color((r << 16) + (g << 8) + b))
        embed.set_image(url=random.choice(randomurl))
        await bot.say(embed=embed)		
		
@bot.command(pass_context=True)
async def savage(ctx):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    gifs = ["https://media.giphy.com/media/s7eezS6vxhACk/giphy.gif", "https://m.popkey.co/5bd499/gK00J_s-200x150.gif", "https://i.imgur.com/XILk4Xv.gif", "https://media.giphy.com/media/KxP8Ik0T4iMa4/giphy.gif", "https://media.giphy.com/media/l378nQdVg2NK5oyqs/giphy.gif", "https://gifimage.net/wp-content/uploads/2017/08/savage-gif-9.gif"]
    embed = discord.Embed(color = discord.Color((r << 16) + (g << 8) + b))
    embed.set_image(url=random.choice(gifs))
    await bot.say(embed=embed)
    await bot.delete_message(ctx.message)

	
@bot.command(pass_context=True)
async def thuglife(ctx):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    gifs = ["https://media.giphy.com/media/kU1qORlDWErOU/giphy.gif", "https://media.giphy.com/media/EFf8O7znQ6zRK/giphy.gif", "https://i.imgur.com/XILk4Xv.gif", "http://www.goodbooksandgoodwine.com/wp-content/uploads/2011/11/make-it-rain-guys.gif", "https://media.giphy.com/media/kU1qORlDWErOU/giphy.gif", "https://i.makeagif.com/media/5-05-2016/61C2G8.gif", "http://image.blingee.com/images19/content/output/000/000/000/819/863226892_1557262.gif"]
    embed = discord.Embed(color = discord.Color((r << 16) + (g << 8) + b))
    embed.set_image(url=random.choice(gifs))
    await bot.say(embed=embed)
    await bot.delete_message(ctx.message)		
		
		
@bot.command(pass_context = True)
async def meme(ctx):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    embed = discord.Embed(title='Random Meme', description='from reddit', color = discord.Color((r << 16) + (g << 8) + b))
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.reddit.com/r/me_irl/random") as r:
            data = await r.json()
            embed.set_image(url=data[0]["data"]["children"][0]["data"]["url"])
            embed.set_footer(text=f'Requested by: {ctx.message.author.display_name}', icon_url=f'{ctx.message.author.avatar_url}')
            embed.timestamp = datetime.datetime.utcnow()
            await bot.say(embed=embed)		
	
@bot.command(pass_context=True)
async def movie(ctx, *, name:str=None):
        r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
        await bot.send_typing(ctx.message.channel)
        if name is None:
                embed=discord.Embed(description = "Please specify a movie, *eg. d?movie Inception*", color = discord.Color((r << 16) + (g << 8) + b))
                x = await bot.say(embed=embed)
                await asyncio.sleep(5)
                return await bot.delete_message(x)
        key = "4210fd67"
        url = "http://www.omdbapi.com/?t={}&apikey={}".format(name, key)
        response = requests.get(url)
        x = json.loads(response.text)
        embed=discord.Embed(title = "**{}**".format(name).upper(), description = "Here is your movie {}".format(ctx.message.author.name), color = discord.Color((r << 16) + (g << 8) + b))
        if x["Poster"] != "N/A":
            embed.set_thumbnail(url = x["Poster"])
            embed.add_field(name = "__Title__", value = x["Title"])
            embed.add_field(name = "__Released__", value = x["Released"])
            embed.add_field(name = "__Runtime__", value = x["Runtime"])
            embed.add_field(name = "__Genre__", value = x["Genre"])
            embed.add_field(name = "__Director__", value = x["Director"])
            embed.add_field(name = "__Writer__", value = x["Writer"])
            embed.add_field(name = "__Actors__", value = x["Actors"])
            embed.add_field(name = "__Plot__", value = x["Plot"])
            embed.add_field(name = "__Language__", value = x["Language"])
            embed.add_field(name = "__Imdb Rating__", value = x["imdbRating"]+"/10")
            embed.add_field(name = "__Type__", value = x["Type"])
            embed.set_footer(text = "Information from the OMDB API")
            await bot.say(embed=embed)		
	
	
@bot.command(pass_context=True)
async def cat(ctx):
        """
        Function: Send random cat picture
        Command: `d?cat`
        Usage Example: `d?cat`
        """
        r = rq.Session().get('http://aws.random.cat/meow')
        if r.status_code == 200:
            emb = discord.Embed(title='Cat')
            emb.set_image(url=r.json()['file'])
            await bot.say(embed=emb)

        if r.status_code != 200:
            emb = discord.Embed(title='Error {}'.format(r.status_code))
            emb.set_image(url='https://http.cat/{}'.format(r.status_code))
            await bot.say(embed=emb)	
	
	
@bot.command(pass_context=True)
async def tweet(ctx, usernamename:str, *, txt:str):
    url = f"https://nekobot.xyz/api/imagegen?type=tweet&username={usernamename}&text={txt}"
    async with aiohttp.ClientSession() as cs:
        async with cs.get(url) as r:
            res = await r.json()
            r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
            embed = discord.Embed(color = discord.Color((r << 16) + (g << 8) + b))
            embed.set_image(url=res['message'])
            embed.title = "{} twitted: {}".format(usernamename, txt)
            await bot.say(embed=embed)	
	
	
	
@bot.command(pass_context=True, aliases=['buddy'])
async def dog(ctx):
        """(d) random dog picture"""
        print("★DOG★")
        isVideo = True
        while isVideo:
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://random.dog/woof.json') as r:
                    res = await r.json()
                    res = res['url']
                    cs.close()
            if res.endswith('.mp4'):
                pass
            else:
                isVideo = False
        em = discord.Embed()
        await bot.say(embed=em.set_image(url=res))	
	
@bot.command(pass_context=True, hidden=True, enabled=True)
async def neko(ctx, nsfw:str="false"):
        """
        Function: Send random neko picture, adding nsfw will send nsfw ones
        Command: `d?neko`
        Usage Example: `d?neko` or `d?neko nsfw`
        """
        if nsfw.lower() == 'nsfw':
            nsfw = 'true'
        else:
            nsfw = 'false'
        img = rq.get(
            'https://nekos.moe/api/v1/random/image?count=1&nsfw={}'.format(nsfw)).json()
        url = 'https://http.cat/200'
        emb = discord.Embed(title='Neko')
        emb.set_image(
            url='https://nekos.moe/image/{}'.format(img['images'][0]['id']))
        await bot.say(embed=emb)		
	
@bot.command(pass_context=True)
async def fox(ctx):
        """
        Function: Send random fox picture
        Command: `d?fox`
        Usage Example: `d?fox`
        """

        emb = discord.Embed(title=None)
        r = rq.Session().get('https://randomfox.ca/floof/')
        if r.status_code == 200:
            emb.set_image(url=r.json()['image'])
            await bot.say(embed=emb)
        if r.status_code != 200:
            emb = discord.Embed(title="Error {}".format(r.status_code))
            emb.set_image(url='https://http.cat/{}'.format(r.status_code))
            await bot.say(embed=emb)	

	
@bot.command(pass_context = True)
async def eightball(ctx):
        '''Answer a question with a response'''

        responses = [
            'It is certain',
            'It is decidedly so',
            'Without a doubt',
            'Yes definitely',
            'You may rely on it',
            'As I see it, yes',
            'Most likely',
            'Outlook good',
            'Yes',
            'Signs point to yes',
            'Reply hazy try again',
            'Ask again later',
            'Better not tell you now',
            'Cannot predict now',
            'Concentrate and ask again',
            'Do not count on it',
            'My reply is no',
            'My sources say no',
            'Outlook not so good',
            'Very doubtful'
        ]

        random_number = random.randint(0, 19)
        if random_number >= 0 and random_number <= 9:
            embed = discord.Embed(color=0x60E87B)
        elif random_number >= 10 and random_number <= 14:
            embed = discord.Embed(color=0xECE357)
        else:
            embed = discord.Embed(color=0xD55050)

        header = 'Magic/Eight ball says...'
        text = responses[random_number]

        embed.add_field(name=header, value=text, inline=True)
        await bot.say(embed=embed)	
	

@bot.command(pass_context = True)
async def happybirthday(ctx, *, msg = None):
    if not msg: await client.say("Please specify a user to wish")
    if '@here' in msg or '@everyone' in msg:
      return
    await bot.say('Happy birthday ' + msg + ' \nhttps://asset.holidaycardsapp.com/assets/card/b_day399-22d0564f899cecd0375ba593a891e1b9.png')
    return		
	
	
	
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


@bot.command(pass_context=True)
async def trans(ctx, *args):
    """Ex: '>trans en->de example' OR '>trans de Beispiel'"""
    if "bugs" in args[0]:
        await client.say("Wraith... bugs is not a language.")
        return

    if len(args[0]) == 2:
        arr = [args[0], "en"]
    else: arr = '{}'.format(args[0]).split('->')
    t = Translator(from_lang=arr[0],to_lang=arr[1])
    await bot.say('```' + t.translate(" ".join(args[1:])) + '```')





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
