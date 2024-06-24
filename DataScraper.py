from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from Player import Player
from Team import Team
from Database import DataBase

class DataScraper:
    def __init__(self):
        self.clubMap = {}
        
    def getTeamLinks(self):
        # This function takes in the transfermarkt premier league webpage and access it
        url = 'https://www.transfermarkt.co.uk/premier-league/startseite/wettbewerb/gb1'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all <td> tags with class "hauptlink no-border-links"
        teamLinks = []
        tdTags = soup.find_all('td', class_='hauptlink no-border-links')
        for tdTag in tdTags:
            teamLinks.append('https://www.transfermarkt.co.uk' + tdTag.find('a')['href'])
        return teamLinks

    def getTeamPlayer(self, teamLink):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(teamLink, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        players = []

        # Find the first table tag, which contains player information
        tableTag = soup.find('table', class_='items')

        # Find all <tr> tags within the player table
        playerTableTags = tableTag.find_all('tr', class_=['odd', 'even'])
        
        for playerTag in playerTableTags:
            tdTags = playerTag.find_all('td', class_='hauptlink')
            for tdTag in tdTags:
                # Check if the euro symbol exists in the text of the td tag
                if '€' in tdTag.get_text():
                    continue  # Skip to the next iteration if the euro symbol is found
                playerName = tdTag.find('a').get_text(strip=True)
                playerLink = 'https://www.transfermarkt.co.uk' + tdTag.find('a')['href']
                players.append(playerLink)
        return players
    
    def getTeamNames(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        teamSet = set()
        urls = self.getTeamLinks()

        # Use ThreadPoolExecutor to concurrently process teams
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit tasks for each team to fetch player data
            future_to_team = {executor.submit(self.processTeamForNames, url, headers): url for url in urls}
            # Iterate over completed futures
            for future in as_completed(future_to_team):
                url = future_to_team[future]
                # Get the result of the future
                team_names = future.result()
                teamSet.update(team_names) 
        return teamSet

    # New method to process each team and extract team names
    def processTeamForNames(self, teamLink, headers):
        playersArray = self.getTeamPlayer(teamLink)
        team_names = set()
        for player in playersArray:
            response = requests.get(player, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            team = self.fetchPlayerTeam(soup)
            if team and "U21" not in team:
                team_names.add(team)
        return team_names
    
    def createPlayer(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        teamLinks = self.getTeamLinks()
        team_data = {}

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_team = {executor.submit(self.processTeam, team, headers): team for team in teamLinks}
            for future in as_completed(future_to_team):
                team = future_to_team[future]
                try:
                    players = future.result()
                    team_data[team] = players
                except Exception as exc:
                    print(f'Team {team} generated an exception: {exc}')

       
    def processTeam(self, teamLink, headers):
        playersLinkArray = self.getTeamPlayer(teamLink)
        
        for player in playersLinkArray:
            response = requests.get(player, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            name = self.fetchPlayerName(soup)
            age = self.fetchPlayerAge(soup)
            height = self.fetchPlayerHeight(soup)
            nationality = self.fetchPlayerNationality(soup)
            team = self.fetchPlayerTeam(soup)
            marketValue = self.fetchPlayerMarketValue(soup)
            position = self.fetchPlayerPosition(soup)
            player = Player(name, age, height, team, marketValue, position, nationality)
            club = self.clubMap[team]
            club.addPlayer(player)

    def fetchPlayerName(self, soup):
        # Narrowing down the parsing
        meta_tag = soup.find('meta', attrs={'name': 'keywords'})
        if meta_tag:
            keywords_content = meta_tag['content']
            name = keywords_content.split(',')[0].strip()
        else:
            tempTag = soup.find('span', class_='info-table__content info-table__content--regular', string='Full name:')
            if tempTag:
                nameTag = tempTag.find_next_sibling('span', class_='info-table__content--bold')
                name = nameTag.get_text(strip=True)
            else:
                tempTag = soup.find('span', class_='info-table__content info-table__content--regular', string='Name in home country:')
                if tempTag:
                    nameTag = tempTag.find_next_sibling('span', class_='info-table__content--bold')
                    name = nameTag.get_text(strip=True)
                else:
                    print("Name not found.")
        return name 

    def fetchPlayerAge(self, soup):
        ageTag = soup.find('span', itemprop='birthDate', class_='data-header__content')
        if ageTag:
            dob = ageTag.get_text(strip=True)
            age = dob.split('(')[-1].replace(')', '').strip()
            return age

    def fetchPlayerHeight(self, soup):
        heightTag = soup.find('span', itemprop='height', class_='data-header__content')
        if heightTag:
            height = heightTag.get_text(strip=True)
            return height
    
    def fetchPlayerNationality(self, soup):
        nationalityTag = soup.find('span', itemprop='nationality', class_='data-header__content')
        if nationalityTag:
            nationality = nationalityTag.get_text(strip=True)
            return nationality
     
    def fetchPlayerTeam(self, soup):
        teamTag = soup.find('span', class_='data-header__club', itemprop='affiliation')
        if teamTag:
            team = teamTag.find('a').get_text(strip=True)
            team = team.replace(" U21" ,"") 
            return team

    def fetchPlayerMarketValue(self, soup):
        marketValueTag = soup.find('a', class_='data-header__market-value-wrapper')
        if marketValueTag:
            euroSymbol = marketValueTag.find('span', class_='waehrung').get_text(strip=True)
            marketValue = marketValueTag.find(string=True, recursive=False).strip()
            marketValueUnit = marketValueTag.find_all('span', class_='waehrung')[1].get_text(strip=True)
            fullMarketValue = f"{euroSymbol}{marketValue}{marketValueUnit}"
            return fullMarketValue

    def fetchPlayerPosition(self, soup):
        positionTag = soup.find('dd', class_='detail-position__position')
        if positionTag:
            position = positionTag.get_text(strip=True)
            return position

    def createDataBase(self):
        clubSet = set()
        for key, val in self.clubMap.items():
            clubSet.add(val)
        dataBase  = DataBase(clubSet)
        dataMap  = dataBase.getData()
        return dataMap
        
        
    
    def createClubs(self):
        teamsArray = self.getTeamNames()
        for team in teamsArray:
            club = Team(team)
            self.clubMap[team] = club
        return self.clubMap
    
    def run(self):
        self.createClubs()
        self.createPlayer()
        dataMap = self.createDataBase()
        return dataMap