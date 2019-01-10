import discord
import asyncio
import youtube_dl
import os
import typing
import json
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import has_permissions 
from discord.utils import get

bot=commands.Bot(command_prefix='.')


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
   await bot.change_presence(game=discord.Game(name='Test'))
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
    embed.set_author(name="Will Ryan of DAGames")
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

  


@bot.event

async def on_reaction_add(reaction, user):
   channel = reaction.message.channel
   await bot.send_message(channel, '{} has added {} to the message: {}'.format(user.name, reaction.emoji, reaction.message.content))
  
@bot.event
async def on_reaction_remove(reaction, user):
   channel = reaction.message.channel
   await bot.send_message(channel, '{} has remove {} from the message: {}'.format(user.name, reaction.emoji, reaction.message.content))
  

@bot.command(pass_context=True)
async def clear(ctx, number):
   if ctx.message.author.server_permissions.administrator:
    mgs = [] #Empty list to put all the messages in the log
    number = int(number) #Converting the amount of messages to delete to an integer
    async for x in bot.logs_from(ctx.message.channel, limit = number):
        mgs.append(x)
    await bot.delete_messages(mgs)

@bot.command(pass_context=True)
async def mute(ctx, member: discord.Member):
    if ctx.message.author.server_permissions.administrator:
        user = ctx.message.author
        role = discord.utils.get(user.server.roles, name="Muted")
        await bot.add_roles(user, role)
        embed=discord.Embed(title="User Muted!", description="**{0}** was muted by **{1}**!".format(member, ctx.message.author), color=0xff00f6)
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
async def kick(ctx, member: discord.Member):
    if ctx.message.author.server_permissions.administrator:
       await bot.kick(member)

        
@bot.command(pass_context=True)
async def ban(ctx, member: discord.Member, days: int = 1):
    if ctx.message.author.server_permissions.administrator:
        await bot.ban(member, days)
    else:
        await bot.say("You don't have permission to use this command.")
        

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
        
        


newUserMessage = """ # customise this to the message you want to send new users
You
can
put
your
multiline
message
here!
"""

@bot.event
async def on_member_join(member):
    print("Recognised that a member called " + member.name + " joined")
    await bot.send_message(member, newUserMessage)
    print("Sent message to " + member.name)

    # give member the steam role here
    ## to do this the bot must have 'Manage Roles' permission on server, and role to add must be lower than bot's top role
    role = discord.utils.get(member.server.roles, name="name-of-your-role")
    await bot.add_roles(member, role)
    print("Added role '" + role.name + "' to " + member.name)        
        
    
  
    
@bot.event
async def on_member_join(member):
    channel = get(member.server.channels, name="general")
    await bot.send_message(channel,"welcome")



    
    
    
    

        
@bot.command(pass_context=True)
async def embed(ctx):
    embed = discord.Embed(title="test", description="my name imran", color=0x00ff00)
    embed.set_footer(text="this is a footer")
    embed.set_author(name="Will Ryan of DAGames")
    embed.add_field(name="This is a field", value="no it isn't", inline=True)
    await bot.say(embed=embed)
   




   
  


   
   
   
    


  




    
bot.run(os.environ['BOT_TOKEN'])
