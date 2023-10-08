from functions import *
import time 

st = time.time() # setting start time

# Getting Match Ids
print('Getting match IDs from HLTV.org...')

# Find last match ID to use as stop
existingMatchIDs = pd.read_csv(r'C:\Users\nando\OneDrive\Documentos\Fernando\Projects\CSGO_Scraper\data\MatchIDs.csv', sep=',', encoding='utf-8')
offset = 100
page = 1

#existingMatchIDs = pd.DataFrame()

while page < 1000:

    newMatchIds = getMatchIDs(offset)
   
    existingMatchIDs = pd.concat([existingMatchIDs, newMatchIds], axis=0)

    existingMatchIDs = existingMatchIDs.astype({'ID': 'int'})

    print('{} new matches tabulated. Total matches: {}.'.format(len(newMatchIds), len(existingMatchIDs)))
    print('Page: {}; Offset: {}'.format(page, offset))

    offset += 100
    page += 1

MatchIDs = existingMatchIDs.drop_duplicates()

print('Total rows: {}. Total rows after drop duplicates: {}. Total removed rows: {}.'.format(len(existingMatchIDs), len(MatchIDs), len(existingMatchIDs) - len(MatchIDs)))

MatchIDs.to_csv('data\MatchIDs.csv', encoding='utf-8', index=False)

et = time.time() # setting end time

print('Total time execution: {} minutes.'.format(round((et - st) / 60), 3))

### TAMBÉM CONSIGO PEGAR OS PLAYERS. EXEMPLO: https://www.hltv.org/player/13290/demonos