import re
from helper import *
import pandas as pd
    
def getMatchIDs(offset):
    
    # Get matches information
   
    print('Get Match IDs from HLTV...')
    html = getHTML("https://www.hltv.org/results?offset={}".format(str(offset)))

    if html is None:
        print("Failed for {}".format(offset))
        return []
    
    # Find where the match information are
    matchIDs = re.findall('"(.*?000"><a href="/matches/.*?)"', html)
    
    # Delete unnecessary data 
    matchIDs = [matchIDs[i].split('/', 2)[-1] for i in range(0, len(matchIDs))]

    # Split in two columns: Id (contains the unique match identifier) and Tittle
    matchIDs = [[matchIDs[i].split('/')[0], matchIDs[i]] for i in range(0, len(matchIDs))]

    # Insert into a pandas DataFrame
    df = pd.DataFrame(matchIDs, columns=['ID', 'Tittle'])

    return df

def getTeamsInfo(soup, html):

    lineups = soup.find_all('div', attrs={'class':'lineups', 'id':'lineups'})
    lines = lineups[0].find_all('div', attrs={'class':'lineup standard-box'})


    teams = list()

    for i, line in enumerate(lines):
        # Find PlayersInfo (teamName, playerName, playerCountry)
        lineup = re.findall(r'alt="([^"]+)"\s+class=', str(line))
        
        team = list() # add teamName and playerNames to a list

        if len(lineup) > 11:
            for l in lineup[:-5]:
                if l not in team:
                    team.append(l)
        else:
            for l in lineup[:-5]:
                team.append(l)

        teamName = team[0]

        teamID = re.findall(r'href="/team/(\d+)/([^"]+)"', str(line))
        teamID = teamID[0][0] + '/' + teamID[0][1] if teamID else ''

        teamRank = re.findall(r'#(\d+)', str(line))
        teamRank = int(teamRank[0])

        teamCountry = re.findall('class="team{}" title=".*\"'.format(i+1), html)
        teamCountry = teamCountry[0].replace("\"", '').split('=')[-1]

        teams.append([teamID, teamName, teamCountry])

    # Create a Pandas DataFrame
    teams = pd.DataFrame(teams, columns=['ID', 'Name', 'Country'])
    
    return teams

def getPlayersInfo(soup):
    lineups = soup.find_all('div', attrs={'class':'lineups', 'id':'lineups'})
    lines = lineups[0].find_all('div', attrs={'class':'lineup standard-box'})

    players = pd.DataFrame() # DataFrame to add players info

    for line in lines:
        lineup = re.findall(r'alt="([^"]+)"\s+class=', str(line))

        player = list() # add players info to a list

        if len(lineup) > 11:
            for l in lineup[:-5]:
                if l not in player:
                    player.append(l)
        else:
            for l in lineup[:-5]:
                player.append(l)

        playersID = [m[0] for m in re.findall(r'href="/player/(\d+)/([^"]+)"', str(line))][:-5]
        playersNickNames = [m[1] for m in re.findall(r'href="/player/(\d+)/([^"]+)"', str(line))][:-5]
        playersName = player[1:]
        playersCountry = lineup[-5:]

        playerDF = pd.DataFrame([playersID, playersNickNames, playersName, playersCountry]).transpose()
        players = pd.concat([players, playerDF], axis=0)

    players.columns = ['ID','NickName','Name','Country']

    return players

def getMaps(soup, html):
    
    matchMaps = list() # list to add maps played 
    # Get map names
    map = re.findall('<div class=\"mapname\">.*</div>', html)
    maps = [map.replace('<div class="mapname">', '').replace('</div>', '') for map in map]
    
    # Get map IDs, you will need this to get stats from all played maps
    m = soup.find_all('div', attrs={'class':'stats-content'})
    mapIDs = re.findall('id=\".*\"', str(m))
    mapIDs = [mapID.replace('id="', '').replace('"', '') for mapID in mapIDs if 'all-content' not in mapID]

    for i in range(0, len(maps)):
        ms = (mapIDs[i], maps[i])

        matchMaps.append(ms)

    return matchMaps