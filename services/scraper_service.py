from typing import List

import requests
from requests import ConnectionError, JSONDecodeError
from scrapy.crawler import CrawlerProcess

import config
from app.settings import settings
from scraper.spiders.games_spider import GamesSpider


class ScraperService:
    def __init__(self):
        api_key = settings.STEAM_API
        self.steam_api_ids_url = f"https://api.steampowered.com/IStoreService/GetAppList/v1?key={api_key}&include_dlc=false&include_software=false&include_videos=false&include_hardware=false&max_results=50000"

    def get_app_ids(self) -> List[int]:
        last_app_id = None
        appids = []

        while True:
            url = self.steam_api_ids_url
            if last_app_id:
                url += f"&last_appid={last_app_id}"

            response = requests.get(url)
            try:
                data = response.json()
            except JSONDecodeError:
                break
            except ConnectionError:
                break
            games = data["response"]["apps"]

            for game in games:
                if (
                    game["appid"] >= config.THRESHOLD_APP_ID
                    and game["price_change_number"] == 0
                ):
                    continue
                appids.append(game["appid"])

            if "have_more_results" in data["response"]:
                last_app_id = data["response"]["last_appid"]
            else:
                break

        return appids

    def scrap(self, filename: str) -> None:
        appids = self.get_app_ids()
        process = CrawlerProcess(
            {
                "FEEDS": {
                    f"{config.DATA_FOLDER}/{filename}.json": {"format": "json"},
                },
                "LOG_ENABLED": False,
            }
        )
        process.crawl(GamesSpider, appids=appids)
        process.start(stop_after_crawl=True, install_signal_handlers=False)


scraper_service = ScraperService()
