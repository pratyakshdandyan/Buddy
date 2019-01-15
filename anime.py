import discord
from discord.ext import commands
import asyncio
import random
import requests as rq
import json


class Anime:
    def __init__(self,bot):
        self.bot=bot


    @commands.command(pass_context=True)
    async def mal(self,con):
        session = rq.Session()
        """SEARCH FOR ANIME USING MyAnimeList. EX: s.mal Mushishi"""
        query = con.message.content[5:]
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
        await self.bot.send_message(con.message.channel, embed=embed)
        await self.bot.send_message(con.message.channel, "**Summary**: {}".format(summary))





    @commands.command(pass_context=True)
    async def char(self,con,*,name):
        session=rq.Session()
        char_query = session.get('https://api.jikan.moe/search/character?q={}&page=1'.format(name)).json()
        char_id = char_query['result'][0]['mal_id']
        char_data = session.get('https://api.jikan.moe/character/{}/pictures'.format(char_id)).json()
        char_name = char_data['name']
        kanji = char_data['name_kanji']
        nick = char_data['nicknames']
        pick = char_data['link_canonical']
        msg=discord.Embed(title='{}:{}'.format(char_name,kanji),description=None)
        msg.add_field(name='Nickname',value=nick)
        msg.set_thumbnail(url=pick)
        await self.bot.send_message(con.message.channel,embed=msg)








def setup(bot):
    bot.add_cog(Anime(bot))
