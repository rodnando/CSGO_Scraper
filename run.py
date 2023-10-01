from functions import *

# Getting Match Ids
print('Getting match IDs from HLTV.org...')

# Find last match ID to use as stop
existingMatchIDs = pd.read_csv(r'C:\Users\nando\OneDrive\Documentos\Fernando\Projects\CSGO_Scraper\data\MatchIDs.csv', sep=',', encoding='utf-8')
offset = 100

existingMatchIDs = pd.DataFrame()

while True:

    #stop = existingMatchIDs['ID'].min()
    #print('New offset: {}. Minimum ID: {}.'.format(offset, stop))

    newMatchIds = getMatchIDs(offset)

    #if stop in newMatchIds['ID'].unique():
    if offset > 1000:
        existingMatchIDs = pd.concat([existingMatchIDs, newMatchIds], axis=0)
        
        print('No new matches found.')
        break
    
    else:
        existingMatchIDs = pd.concat([existingMatchIDs, newMatchIds], axis=0)
        offset += 100

        existingMatchIDs = existingMatchIDs.astype({'ID': 'int'})

        print('{} new matches tabulated. Total matches: {}.'.format(len(newMatchIds), len(existingMatchIDs)))


MatchIDs = existingMatchIDs.drop_duplicates()

MatchIDs.to_csv('data\MatchIDs.csv', encoding='utf-8', index=False )

print('Total rows: {}. Total rows after drop duplicates: {}. Total removed rows: {}.'.format(len(existingMatchIDs), len(MatchIDs), len(existingMatchIDs) - len(MatchIDs)))



### TAMBÉM CONSIGO PEGAR OS PLAYERS. EXEMPLO: https://www.hltv.org/player/13290/demonos