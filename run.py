from functions import *
from helper import tabulate
import pandas as pd
import time 

# Find last match ID to use as stop
existingMatchIDs = pd.read_csv(r'data\matchIDs.csv', sep=',', encoding='utf-8')
existingOverview = pd.read_csv(r'data\matchOverview.csv', sep=',', encoding='utf-8')

# Getting matchIds without overview
newMatches = list()
overv = existingOverview.MatchID.drop_duplicates().values.tolist()
for m in existingMatchIDs.Tittle:
    if int(m.split('/')[0]) not in overv:
        newMatches.append(m)

track = 1
start_time = time.time() # variable to tracking time execution

for matchID in newMatches:
    print('Start execution number {}...'.format(track))
    # Complete matches URL with the match ID
    print('Getting match infos for {}...'.format(matchID))
    url = f'https://www.hltv.org/matches/{matchID}'
    html, soup = getDriverHTML(url)

    print('Getting teams info...') 
    try:    
        teams = getTeamsInfo(soup, html)
        print('Saving data...')
        tabulate('teams', teams)
    except Exception as e:
        print(e)
    
    print('Getting players info...')
    try:
        players = getPlayersInfo(soup)
        print('Saving data...')
        tabulate('players', players)
    except Exception as e:
        print(e)

    print('Getting match overview...')
    try:
        overview = getMatchOverview(soup, html, matchID)
        print('Saving data...')
        tabulate("matchOverview", overview)
    except Exception as e:
        print(e)
    
    print('Getting match infos...')
    try:
        matchInfo = getMatchInfos(soup, html, matchID)
        print('Saving data...')
        tabulate("matchInfos", matchInfo)
    except Exception as e:
        print(e)
    
    print('Getting economy infos...')
    try:
        economy = getEconomyOverview(soup, html, matchID, overview, teams)
        print('Saving...')
        tabulate("matchEconomy", economy)
    except Exception as e:
        print(e)

    print('Execution for {} ended. Total time execution: {} minutes.'.format(matchID, round((time.time() - start_time)/60, 3)))

    track += 1