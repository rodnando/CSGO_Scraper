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

def getLineups(soup, matchID):
    lineups = soup.find_all('div', attrs={'class':'lineups', 'id':'lineups'})
    lines = lineups[0].find_all('div', attrs={'class':'lineup standard-box'})

    Lineups = pd.DataFrame() # list to add players info

    for line in lines:
        lineup = re.findall(r'alt="([^"]+)"\s+class=', str(line))

        playersID = [m[0] for m in re.findall(r'href="/player/(\d+)/([^"]+)"', str(line))][:-5]
        
        teamID = re.findall(r'href="/team/(\d+)/([^"]+)"', str(line))
        teamID = teamID[0][0] + '/' + teamID[0][1] if teamID else ''

        teamRank = re.findall(r'#(\d+)', str(line))
        teamRank = int(teamRank[0])

        lineup = pd.DataFrame(playersID, columns=['PlayerID'])
        lineup['TeamID'] = teamID
        lineup['TeamRank'] = teamRank
        lineup['MatchID'] = matchID.split('/')[0]

        Lineups = pd.concat([Lineups, lineup], axis=0)

    return Lineups

def getMatchInfos(soup, html, matchID):
    
    # Get maps info to query data from each map 
    maps = getMaps(soup, html)

    # Classes to query inside map infos, total stats, total stats CT side, total stats TR side
    sides = ['table totalstats','table ctstats hidden','table tstats hidden']
    sideNames = ['Total','CT','TR']

    matchInfo = pd.DataFrame()

    for map in maps:
        matchInfos = soup.find('div', attrs={'class':'stats-content', 'id':map[0]})

        # Get lineups to use as a main table to do joins
        lineups = getLineups(soup, matchID)
        lineups['MapName'] = map[1]
        
        # Looping to get stats from each side and the total 
        for i, side in enumerate(sides):
            stats = matchInfos.find_all('table', attrs={'class':side})

            # Player ID
            playersID = re.findall(r'/player/(\d+)/([^/]+)', str(stats))
            playerID = list()
            for r in playersID:
                playerID.append(r[0])
            
            # Player Score
            score = re.findall(r'class="plus-minus text-center gtSmartphone-only"><span class="[^"]*">(.*?)</span>', str(stats))
            score = [int(score) for score in score]

            # Kills and Deaths (KD)
            kds = re.findall(r'class="kd text-center">(\d+-\d+)</td>', str(stats))
            k = list()
            d = list()
            for kd in kds:
                k.append(int(kd.split('-')[0]))
                d.append(int(kd.split('-')[1]))
            
            # ADR
            adr = re.findall(r'<td class="adr text-center">(\d+\.\d+)</td>', str(stats))
            ADR = [float(adr) for adr in adr]

            # KAST
            kast = re.findall(r'<td class="kast text-center">([0-9]+\.[0-9]+%)</td>', str(stats))
            KAST = [round(float(kast.split('.')[0]) / 100, 2) for kast in kast]

            # Rating
            ratings = re.findall(r'<td class="rating text-center">([0-9]+\.[0-9]+)</td>', str(stats))
            rating = [round(float(rating), 2) for rating in ratings]

            matchsInfo = [playerID, k, d, score, ADR, KAST, rating]
            matchsInfo = pd.DataFrame(matchsInfo).transpose()
            matchsInfo.columns = ['PlayerID', f'{sideNames[i]}_Kills', f'{sideNames[i]}_Deaths', f'{sideNames[i]}_Score', f'{sideNames[i]}_ADR', f'{sideNames[i]}_KAST', f'{sideNames[i]}_Rating']

            lineups = pd.merge(lineups, matchsInfo, on='PlayerID', how='left')
        
        matchInfo = pd.concat([matchInfo, lineups], axis=0)

    return matchInfo