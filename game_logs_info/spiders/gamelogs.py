# -*- coding: utf-8 -*-
import scrapy
import re

def cleanup(input_string):
    # Remove all unnecessary \t \r \n and spaces
    if input_string:
        return re.sub(r'[\\r\\n\\t@]', '', input_string).strip()

class GamelogsSpider(scrapy.Spider):
    name = 'gamelogs'
    allowed_domains = ['www.nfl.com']
    start_urls = ['http://www.nfl.com/players/search?category=lastName&filter=A&playerType=historical']

    def parse(self, response):
        players_list = response.xpath("//*[@id='result']//*[@class='tbdy']/a")
        for players in players_list:
            player_link = players.xpath(".//@href").get()
            yield response.follow(url=player_link, callback=self.parse_players_profile)
        # Deal with Pagination
        next_page = response.xpath("//span[@class='linkNavigation floatRight']/a/@href").get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse)

    # def parse_players_profile(self, response):
    #     profile_page = response.xpath("(//*[@id='player-profile-tabs'])/ul/li[3]/a/@href").get()
    #     yield response.follow(url=profile_page, callback=self.parse_players_info)

    def parse_players_profile(self, response):
        profile_link = response.urljoin("gamelogs")
        yield scrapy.Request(url=profile_link, callback=self.parse_players_info)

    def parse_players_info(self, response):
        players_name = cleanup(response.xpath("//span[@class='player-name']/text()").get())
        years = response.xpath("//*[@id='game-log-year']/strong")
        for year in years:
            year_name = year.xpath(".//text()").get()
        all_seasons = response.xpath("(//*[@class='data-table1'])/thead/tr[1]/td[1]")
        for season in all_seasons:
            season_name = season.xpath(".//text()").get()
        all_rows = response.xpath("(//*[@class='data-table1']/tbody/tr[1])")
        for rows in all_rows:
            game_week = rows.xpath(".//td[1]/text()").get()
            game_date = rows.xpath(".//td[2]/text()").get()
            opponent = cleanup(rows.xpath(".//td[3]/a/text()").get())
            g = rows.xpath(".//td[5]/text()").get()
            gs = rows.xpath(".//td[6]/text()").get()

        yield {
            "Player Name": players_name,
            "Year": year_name,
            "Season": season_name,
            "Week": game_week,
            "Date": game_date,
            "Opponent": opponent,
            "Game": g,
            "Game Start": gs,
            "URL": response.url
        }
