import re
from typing import List

import scrapy
from tqdm import tqdm

from scraper.items import GameItem


class GamesSpider(scrapy.Spider):
    name = "games_spider"
    allowed_domains = ["store.steampowered.com"]
    start_url = "https://store.steampowered.com/app"

    def __init__(self, appids: List[int] = None, *args, **kwargs):
        super(GamesSpider, self).__init__(*args, **kwargs)
        self.appids = appids

    def start_requests(self):
        for appid in tqdm(self.appids):
            url = f"{self.start_url}/{str(appid)}?cc=us&l=en"
            yield scrapy.Request(
                url=url,
                callback=self.parse_games,
                cookies={
                    "wants_mature_content": "1",
                    "birthtime": "189302401",
                    "lastagecheckage": "1-January-1976",
                },
            )

    def parse_games(self, response, **kwargs):
        appid = response.xpath('//input[@id="review_appid"]/@value').extract()

        if len(appid) == 0:
            appid = response.xpath(
                '//div[@id="responsive_page_template_content"]/div[@class="game_page_background game"]/@data-miniprofile-appid'
            ).extract()

        title = response.xpath('//div[@id="appHubAppName"]/text()').extract()

        if len(title) == 0:
            title = ["NoTitle!"]

        tags = list(
            map(
                lambda x: x.strip(),
                response.xpath(
                    '//div[@class="glance_tags popular_tags"]/a/text()'
                ).extract(),
            )
        )

        if len(tags) == 0:
            tags = ["No Tags"]

        reviews = response.xpath(
            '//div[@id="userReviews"]/div[@class="user_reviews_summary_row"]/div/meta[@itemprop="reviewCount"]/@content'
        ).extract()

        if len(reviews) == 0:
            reviews = [0]

        reviews_fancy = response.xpath(
            '//div[@id="userReviews"]/div[div[@class="subtitle column all"]]/div/span[@class="nonresponsive_hidden responsive_reviewdesc"]/text()'
        ).extract()

        if len(reviews_fancy) == 0 or "%" not in reviews_fancy[0]:
            reviews_fancy = "0%"
        else:
            reviews_fancy = re.findall(r"\d+%", reviews_fancy[0])[0]

        price = response.xpath(
            '//div[@id="game_area_purchase"]/div[@class="game_area_purchase_game_wrapper"]/div/div[@class="game_purchase_action"]/div/div[@class="game_purchase_price price"]/@data-price-final'
        ).extract()

        is_free = response.xpath('//div[@id="freeGameBtn"]/text()').extract()

        if len(is_free) > 0:
            price = [0]

        if len(price) == 0:
            price = response.xpath(
                '//div[@id="game_area_purchase"]/div[@class="game_area_purchase_game_wrapper"]/div[@class="game_area_purchase_game"]/div[@class="game_purchase_action"]/div/div[@class="discount_block game_purchase_discount"]/div[@class="discount_prices"]/div[@class="discount_original_price"]/text()'
            ).extract()

            price = ["".join([s for s in list(p) if s.isdigit()]) for p in price]

        price = list(map(int, price))

        release_date = response.xpath(
            '//div[@id="game_highlights"]/div[@class="rightcol"]/div/div[@class="glance_ctn_responsive_left"]/div[@class="release_date"]/div[@class="date"]/text()'
        ).extract()

        if len(release_date) == 0:
            release_date = ["No Release Date"]

        try:
            appid = int(appid[0])
        except:
            appid = -1

        game_item = GameItem()
        game_item["appid"] = appid
        game_item["title"] = title[0]
        game_item["tags"] = ", ".join(tags)
        game_item["reviews"] = int(reviews[0])
        game_item["price"] = min(price)
        game_item["release_date"] = release_date[0]
        game_item["reviews_fancy"] = reviews_fancy

        return game_item
