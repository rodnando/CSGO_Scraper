import re
from helper import *
import pandas as pd
    
def getMatchIDs(offset):
    # This function goal is to get match IDs in each page on HLTV.org
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
    # This function goal is to get teams info
    lineups = soup.find_all('div', attrs={'class':'lineups', 'id':'lineups'})
    lines = lineups[0].find_all('div', attrs={'class':'lineup standard-box'})

    if len(lines) < 1:
        raise Exception('Fail to get data. Return is none.')

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
        teamNick = teamID[0][1] if teamID else ''
        teamID = teamID[0][0] if teamID else ''

        teamRank = re.findall(r'#(\d+)', str(line))
        teamRank = int(teamRank[0])

        teamCountry = re.findall('class="team{}" title=".*\"'.format(i+1), html)
        teamCountry = teamCountry[0].replace("\"", '').split('=')[-1]

        teams.append([teamID,teamNick,teamName,teamCountry])

    # Create a Pandas DataFrame
    teams = pd.DataFrame(teams, columns=['ID', 'Nick', 'Name', 'Country'])
    
    return teams

def getPlayersInfo(soup):
    # This function goal is to get players info
    lineups = soup.find_all('div', attrs={'class':'lineups', 'id':'lineups'})
    lines = lineups[0].find_all('div', attrs={'class':'lineup standard-box'})

    if len(lines) < 1:
        raise Exception('Fail to get data. Return is none.') 

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
    # This function goal is to get maps played in each match
    matchMaps = list() # list to add maps played 
    # Get map names
    map = re.findall('<div class=\"mapname\">.*</div>', html)
    maps = [map.replace('<div class="mapname">', '').replace('</div>', '') for map in map]
    
    # Get map IDs, you will need this to get stats from all played maps
    m = soup.find_all('div', attrs={'class':'stats-content'})
    mapIDs = re.findall('id=\".*\"', str(m))
    mapIDs = [mapID.replace('id="', '').replace('"', '') for mapID in mapIDs if 'all-content' not in mapID]

    # Drop maps not played
    maps = maps[:len(mapIDs)]

    for i in range(0, len(maps)):
        ms = (mapIDs[i], maps[i])

        matchMaps.append(ms)

    return matchMaps

def getLineups(soup, matchID):
    # This function goal is to get team lineups (player for each team)
    lineups = soup.find_all('div', attrs={'class':'lineups', 'id':'lineups'})
    lines = lineups[0].find_all('div', attrs={'class':'lineup standard-box'})

    if len(lines) < 1:
        raise Exception('Fail to get data. Return is none.')

    Lineups = pd.DataFrame() # list to add players info

    for line in lines:
        lineup = re.findall(r'alt="([^"]+)"\s+class=', str(line))

        playersID = [m[0] for m in re.findall(r'href="/player/(\d+)/([^"]+)"', str(line))][:-5]
        
        teamID = re.findall(r'href="/team/(\d+)/([^"]+)"', str(line))
        teamID = teamID[0][0] if teamID else ''

        teamRank = re.findall(r'#(\d+)', str(line))
        teamRank = int(teamRank[0])

        lineup = pd.DataFrame(playersID, columns=['PlayerID'])
        lineup['TeamID'] = teamID
        lineup['TeamRank'] = teamRank
        lineup['MatchID'] = matchID.split('/')[0]

        Lineups = pd.concat([Lineups, lineup], axis=0, ignore_index=True)

    return Lineups

def getMatchInfos(soup, html, matchID):
    # This function goal is to extract match info for each map in each match
    # Get maps info to query data from each map 
    maps = getMaps(soup, html)

    # Classes to query inside map infos, total stats, total stats CT side, total stats TR side
    sides = ['table totalstats','table ctstats hidden','table tstats hidden']
    sideNames = ['Total','CT','TR']

    matchInfo = pd.DataFrame()

    for map in maps:
        matchInfos = soup.find('div', attrs={'class':'stats-content', 'id':map[0]})

        if len(matchInfos) < 1:
            raise Exception('Fail to get data about match infos. Return is none.')
        
        # Get lineups to use as a main table to do joins
        lineups = getLineups(soup, matchID)
        lineups['MapName'] = map[1]
        
        # Looping to get stats from each side and the total 
        for i, side in enumerate(sides):
            stats = matchInfos.find_all('table', attrs={'class':side})

            if len(stats) < 1:
                raise Exception(f'Fail to get data from side {side}. Return is none.')

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
        
        matchInfo = pd.concat([matchInfo, lineups], axis=0, ignore_index=True)

    return matchInfo

def getMatchOverview(soup, html, matchID):
    # This function goal is to get the match overview for each map, like winner, final score, etc.
    # Get teams to add to a DataFrame 
    teams = getTeamsInfo(soup, html)
    teams = [teams for teams in teams['ID']]

    MatchOverview = pd.DataFrame()

    matchOverview = soup.find_all('div', attrs={'class':'played'})
    
    if len(matchOverview) < 1:
        raise Exception('Fail to get data. Return is none.')
    
    matchOverviews = concat_tags(matchOverview)

    for i, match in enumerate(matchOverviews):
        mapName = re.findall(r'map-name-holder"><img alt="([^"]+)" class="minimap"', str(match))
        mapName = mapName[0]

        # Get match result (win/lost) and pick. If team 1 win this will be set True, the same if team 1 pick the map
        finalResult = re.findall(r'class="results-left.*\"', str(match))
        team1Win = 'won' in finalResult[0]
        team1Pick = 'pick' in finalResult[0]

        # Get final score
        finalScore = re.findall(r'<div class="results-team-score">(\d+)</div>', str(match))
        
        # Get half results
        total_halfs = re.findall(r'\((.*?)\)', str(match))
        halfs = total_halfs[0].split(';')

        startSide = 'CT' if 'ct' in halfs[0].split(':')[0] else 'TR'

        if len(total_halfs) > 1:
            overtime = re.findall(r'<span>(\d+)</span>', str(total_halfs[1]))

            team1_over = int(overtime[0])
            team2_over = int(overtime[1])
        else:
            team1_over = 0
            team2_over = 0

        columns = ['MatchID','MapName','Team1','Team2','Team1_Pick','Team1_Win','Team1_Final_Score','Team2_Final_Score','Halfs_Played','Team1_Start_Side']
        result = [matchID.split('/')[0],mapName,int(teams[0]),int(teams[1]),team1Pick,team1Win,int(finalScore[0]),int(finalScore[1]),len(halfs),startSide]

        for i, half in enumerate(halfs):
            results = re.findall(r'class="(ct|t)">(\d+)</span>', str(half))
            result.append(int(results[0][1]))
            result.append(int(results[1][1]))

            columns.append(f'Team1_Half{i+1}_Score')
            columns.append(f'Team2_Half{i+1}_Score')

        result.append(team1_over)
        result.append(team2_over)

        columns.append('Team1_OT_Score')
        columns.append('Team2_OT_Score')

        # Create a PataFrame to merge with the final DataFrame
        mapOverview = pd.DataFrame(result).transpose()
        mapOverview.columns = columns

        MatchOverview = pd.concat([MatchOverview, mapOverview], axis=0, ignore_index=True)
    
    return MatchOverview

def getEconomyOverview(soup, html, matchID, overview, teams):
    # Define final DF with the economic infos
    economy_info = pd.DataFrame()

    # Define params
    id = matchID.split('/')[0]
    
    # Get Overview
    over_id = overview.loc[overview['MatchID'] == int(id)]
    over_id_ = over_id[['MatchID', 'Team1', 'Team2']].drop_duplicates()

    # Get teams nicknames
    match_params_df = over_id_.merge(teams, left_on='Team1', right_on='ID').merge(teams, left_on='Team2', right_on='ID')

    match_params = match_params_df[['Team1', 'Team2', 'Nick_x', 'Nick_y']].drop_duplicates().values.tolist()[0]
    versus = match_params[2] + '-vs-' + match_params[3]

    # Get map info from match page
    maps = getMaps(soup, html)

    for Map in maps:
        mapName = Map[1]
        mapID = Map[0].split('-')[0]

        url = f'https://www.hltv.org/stats/matches/economy/mapstatsid/{mapID}/{versus}'
        
        html, soup = getDriverHTML(url)
        
        # Checking if there is economy info for this map
        problem = soup.find('div', attrs={'class':'standard-box padding'})
        
        if 'Economy not available' not in str(problem):
            # Get rounds overview info
            rounds_break = soup.find_all('div', attrs={'class':'col standard-box stats-rows'})

            rounds_overview = list()
            columns = ['Eco_Rounds','Eco_Rounds_Wons','Semi_Eco_Rounds','Semi_Eco_Rounds_Wons','Semi_Buy_Rounds','Semi_Buy_Rounds_Wons','Full_Buy_Rounds','Full_Buy_Rounds_Wons']

            rounds_overview = list()
            columns = ['MatchID','TeamID','MapName','Eco_Rounds','Eco_Rounds_Wons','Semi_Eco_Rounds','Semi_Eco_Rounds_Wons','Semi_Buy_Rounds','Semi_Buy_Rounds_Wons','Full_Buy_Rounds','Full_Buy_Rounds_Wons']

            for i, round in enumerate(rounds_break):
                results = re.findall(r'title="Played">(\d+)<span title="Won"> \((\d+)\)', str(round))

                if i == 0:
                    rounds_over = [id, match_params[0], mapName]
                else:
                    rounds_over = [id, match_params[1], mapName]

                for r in results:
                    rounds_over.append(r[0]) # Played
                    rounds_over.append(r[1]) # Won

                rounds_overview.append(rounds_over)

            equip_info = soup.find_all('tr', attrs={'class':'team-categories'})

            if len(equip_info) % 2 != 0:
                print('Error!')

            equip1_info = list()
            equip2_info = list()

            for i in range(0, len(equip_info)):
                if i % 2 == 0:
                    equip1_info.append(str(equip_info[i]))
                else:
                    equip2_info.append(str(equip_info[i]))

            if len(equip1_info) != len(equip2_info):
                print('Error!')

            for info in equip1_info:
                results = re.findall(r'title="Equipment value: (\d+)"><img class="equipment-category(.*?)" src="', str(info))
                
                for i, r in enumerate(results):
                    rounds_overview[0].append(r[0])
                    rounds_overview[0].append(False if 'lost' in r[1].strip() else True)

            for info in equip2_info:
                results = re.findall(r'title="Equipment value: (\d+)"><img class="equipment-category(.*?)" src="', str(info))
                
                for i, r in enumerate(results):
                    rounds_overview[1].append(r[0])
                    rounds_overview[1].append(False if 'lost' in r[1].strip() else True)

            # Add new columns (spent and result)
            for i in range(0, int((len(rounds_overview[0])-11) / 2)):
                columns.append(f'Round{i+1}_Spent')
                columns.append(f'Round{i+1}_Result')

            economy = pd.DataFrame(rounds_overview)
            economy.columns = columns

            economy_info = pd.concat([economy_info, economy])
        else:
            print('No results for map {} in macthID: {}!'.format(mapName, matchID))

    return economy_info