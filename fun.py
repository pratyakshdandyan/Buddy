import discord
from discord.ext import commands
import asyncio
import time
import datetime
import json
import requests as rq
import random





class Fun:
    def __init__(self,bot):
        self.bot=bot


    @commands.command(pass_context=True)
    async def dog(self,con):
        r = rq.Session().get('https://random.dog/woof.json').json()
        emb = discord.Embed(title='Dog')
        emb.set_image(url=r['url'])
        await self.bot.send_message(con.message.channel, embed=emb)


    @commands.command(pass_context=True)
    async def say(self,con, *, msg):
        message = await self.bot.send_message(con.message.channel, "{}".format(msg))
        await asyncio.sleep(120)
        await self.bot.delete_message(message)


    @commands.command(pass_context=True)
    async def randomshow(self,con):
        session = rq.Session()
        url = 'https://tv-v2.api-fetch.website/random/show'
        r = session.get(url).text
        r_json = json.loads(r)
        name = r_json['title']
        year = r_json['year']
        img = r_json['images']['poster']
        await self.bot.send_message(con.message.channel, "**Name**: {}\n**Year**: {}\n**Poster**: {}".format(name, year, img))


    @commands.command(pass_context=True)
    async def catfact(self,con):
        session = rq.Session()
        fact_id = random.randint(0, 127)
        r = session.get(
            'https://jsonblob.com/api/d02645c2-151b-11e9-8960-c9ff29aada09')
        if r.status_code != 200:
            await self.bot.send_message(con.message.channel, "**Something went wrong please try again later**")
        if r.status_code == 200:
            try:
                await self.bot.send_message(con.message.channel, "**{}**\n**Fact ID** `{}`".format(r.json()['animals']['cats'][fact_id], fact_id))
            except:
                await self.bot.send_message(con.message.channel, "**Something went wrong while sending the fact\nPlease try again later**")


    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=2, type=commands.BucketType.channel)
    async def randomanime(self,con):
        session = rq.Session()
        """GENERATES A RANDOM ANIME TITLE WITH 10 SECOND COOL DOWN. EX: s.randomanime"""
        r = rq.get('https://tv-v2.api-fetch.website/random/anime').json()
        title = r['title']
        mal_id = r['mal_id']
        genres = r['genres']
        url2 = 'https://api.jikan.moe/anime/{}/stats/'.format(mal_id)
        r2 = session.get(url2).text
        r2j = json.loads(r2)
        summary = r2j['synopsis']
        await self.bot.send_message(con.message.channel, "**Title**: {}\n**Genres**: {}\n**Synopsis**: {}".format(title, genres, summary))


    @commands.command(pass_context=True)
    async def randommovie(self,con):
        session = rq.Session()
        """GENERATES A RANDOM MOVIE TITLE. EX: s.randommovie"""
        movie = session.get('https://tv-v2.api-fetch.website/random/movie')
        if movie.status_code == 200:
            rest = movie.text
            rq_json = json.loads(rest)
            title = rq_json['title']
            summary = rq_json['synopsis']
            runtime = rq_json['runtime']
            genres = rq_json['genres']
            gen = " ".join(genres[1:])
            await self.bot.send_message(con.message.channel, "**Title**: {}\n**Genres**: {}\n**Length*: {} Minutes\n**Synopsis**: {}".format(title, gen, runtime, summary))


    @commands.command(pass_context=True)
    async def cat(self,con):
        r = rq.Session().get('http://aws.random.cat/meow').json()
        emb = discord.Embed(title='Cat')
        emb.set_image(url=r['file'])
        await self.bot.send_message(con.message.channel, embed=emb)


    @commands.command(pass_context=True)
    async def cookie(self,con, user: discord.Member):
        amount = random.randint(1, 15)
        await self.bot.send_message(con.message.channel, "{0} you got {2} cookies from {1}".format(user.mention, con.message.author.name, amount))


    @commands.command(pass_context=True)
    async def neko(self,con, *, nsfw='None'):
        if nsfw.lower() == 'nsfw':
            session = rq.Session()
            r = session.get(
                'https://nekos.moe/api/v1/random/image?count=1&nsfw=true').json()
            id = r['images'][0]['id']
            msg = discord.Embed(title='Neko')
            msg.set_image(url='https://nekos.moe/image/{}'.format(id))
            try:
                msg.set_footer(text='Artist: {}'.format(r['images'][0]['artist']))
            except KeyError:
                pass
            try:
                await self.bot.send_message(con.message.channel, embed=msg)
            except:
                await self.bot.send_message(con.message.author, embed=msg)
        elif nsfw == 'None' and 'nsfw' not in nsfw.lower():
            session = rq.Session()
            r = session.get(
                'https://nekos.moe/api/v1/random/image?count=1&nsfw=false').json()
            id = r['images'][0]['id']
            msg = discord.Embed(title='Neko')
            msg.set_image(url='https://nekos.moe/image/{}'.format(id))
            try:
                msg.set_footer(text='Artist: {}'.format(r['images'][0]['artist']))
            except:
                pass
            try:
                await self.bot.send_message(con.message.channel, embed=msg)
            except:
                await self.bot.send_message(con.message.author, embed=msg)


    @commands.command(pass_context=True)
    async def bunnyfact(self,con):
        session = rq.Session()
        fact_id = random.randint(0, 17)
        r = session.get(
            'https://jsonblob.com/api/ea1a1a28-151b-11e9-8960-6d585dac6621')
        if r.status_code != 200:
            try:
                await self.bot.send_message(con.message.channel, "Somethign went wrong, please try again later")
            except:
                await self.bot.send_message("Something went wrong, please try again later")
        if r.status_code == 200:
            try:
                await self.bot.send_message(con.message.channel, "**{}**\n**Fact ID** `{}`".format(r.json()['animals']['bunny'][fact_id], fact_id))
            except:
                await self.bot.send_message("**{}**\n**Fact ID** `{}`".format(r.json()['animals']['bunny'][fact_id], fact_id))


    @commands.command(pass_context=True)
    async def pifact(self,con):
        session = rq.Session()
        fact_id = random.randint(0, 49)
        r = session.get(
            'https://jsonblob.com/api/ea1a1a28-151b-11e9-8960-6d585dac6621')
        if r.status_code != 200:
            await self.bot.send_message(con.message.channel, "**Something went wrong while trying to get the fact\nPlease try again later**")
        if r.status_code == 200:
            try:
                await self.bot.send_message(con.message.channel, "**{}**\n**Fact ID** `{}`".format(r.json()['math']['pi'][fact_id], fact_id))
            except:
                await self.bot.send_message(con.message.channel, "**Something went wrong while trying to send the fact\nPlease try again later**")


    @commands.command(pass_context=True)
    async def dogfact(self,con):
        session = rq.Session()
        fact_id = random.randint(0, 100)
        r = session.get(
            'https://jsonblob.com/api/ea1a1a28-151b-11e9-8960-6d585dac6621')
        if r.status_code != 200:
            await self.bot.send_message(con.message.channel, "**Somethign went wrong retrieving the fact\nPlease try again later.**")
        if r.status_code == 200:
            try:
                await self.bot.send_message(con.message.channel, "**{}**\n**Fact ID** `{}`".format(r.json()['animals']['dogs'][fact_id], fact_id))
            except:
                await self.bot.send_message(con.message.channel, "**Something went wrogn while trying to send the fact\nPlease try again later.**")




    @commands.command(pass_context=True)
    @commands.cooldown(rate=10, per=1, type=commands.BucketType.channel)
    async def game(self,con, *,msg):
        """CHANGES THE PLAYING STATUS OF THE BOT. EX: s.game OSU!"""
        await self.bot.change_presence(game=discord.Game(name=msg))


    @commands.command(pass_context=True)
    @commands.cooldown(rate=10, per=1, type=commands.BucketType.channel)
    async def listening(self,con, *,msg):
        await self.bot.change_presence(game=discord.Game(name=msg,type=2))


    @commands.command(pass_context=True)
    @commands.cooldown(rate=10, per=1, type=commands.BucketType.channel)
    async def watching(self,con, *,msg):
        await self.bot.change_presence(game=discord.Game(name=msg,type=3))


    @commands.command(pass_context=True)
    async def bunny(self,con):
        msg = discord.Embed(title='Bunny')
        msg.set_image(url='https://www.kurusaki.com/Rab/{}.jpg'.format(random.randint(1, 89)))
        await self.bot.send_message(con.message.channel, embed=msg)








def setup(bot):
    bot.add_cog(Fun(bot))
