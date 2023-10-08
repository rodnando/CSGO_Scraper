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

    for i, l in enumerate(lines):
        # Find PlayersInfo (teamName, playerName, playerCountry)
        lineup = re.findall(r'alt="([^"]+)"\s+class=', str(lines[i]))
        
        team = list() # add teamName and playerNames to a list

        if len(lineup) > 11:
            for l in lineup[:-5]:
                if l not in team:
                    team.append(l)
        else:
            for l in lineup:
                team.append(l)

        teamName = team[0]

        teamID = re.findall(r'href="/team/(\d+)/([^"]+)"', str(lines[i]))
        teamID = teamID[0][0] + '/' + teamID[0][1] if teamID else ''

        teamRank = re.findall(r'#(\d+)', str(lines[i]))
        teamRank = int(teamRank[0])

        teamCountry = re.findall('class="team{}" title=".*\"'.format(i+1), html)
        teamCountry = teamCountry[0].replace("\"", '').split('=')[-1]

        teams.append([teamID, teamName, teamCountry])

        # Create a Pandas DataFrame
        df = pd.DataFrame(teams, columns=['ID', 'TeamName', 'TeamCountry'])
    
    return df