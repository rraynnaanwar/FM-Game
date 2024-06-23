import sys
import os
from DataScraper import DataScraper
from Database import DataBase
sys.stdout.reconfigure(encoding='utf-8')

scraper = DataScraper()
dataMap = scraper.run()


script_dir = os.path.dirname(os.path.abspath(__file__))
filePath = os.path.join(script_dir, "players.txt")

with open(filePath, 'w', encoding='utf-8') as file:
    for key, val in dataMap.items():

        file.write(f"{key}\n")
        playersArray = val

        for player in playersArray:
            file.write(f"{player}\n")