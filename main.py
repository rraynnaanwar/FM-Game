import sys
from DataScraper import DataScraper
from Database import DataBase
sys.stdout.reconfigure(encoding='utf-8')

scraper = DataScraper()
scraper.createPlayer()
players= scraper.getPlayers()
for player in players:
    print(player)
    # test committ