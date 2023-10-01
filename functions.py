import re
from helper import *
import pandas as pd
    
def getMatchIDs(offset):
    
    # Get matches information
   
    print('Get Match IDs from HLTV...')
    html = getHTML("https://www.hltv.org/results?offset={}".format(str(offset)))

    if html is None:
        print("Failed for %s" % (offset))
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