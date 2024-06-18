import sys
from DataScraper import DataScraper
from Database import DataBase
sys.stdout.reconfigure(encoding='utf-8')

scraper = DataScraper()
dataMap = scraper.run()
for key, val in dataMap.items():
    print(key)
    playersArray = val
    for player in playersArray:
        print(player)