"""
Runs multiple 2-player games, alternating player pairings.

Place this file in the same directory as quoridor.py
Usage: multiplegames.py player1 player2 [num games per pairing] [animation speed] [cfgfile]

Author: Adam Oest (amo9149@rit.edu)
"""

import sys, itertools, operator, random, subprocess

def main():
    """Run the engine and start the game"""
    global game,playerWins,MAX_GAMES
    
    if len(sys.argv) < 3:
        print('Usage: multiplegames.py player1 player2 [num games] [cfgfile]')
        sys.exit(0)
    
    # Number of times all pairings are repeated
    MAX_GAMES = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    
    print("Will play %s games" % MAX_GAMES)
        
    ###### MAIN SCRIPT ######         
    players = [sys.argv[1],sys.argv[2]]    
    
    # build player win dictionary
    game = 1
    playerWins = {}
    for player in players:
        if player.strip()in playerWins.keys():
            print('Player names must be unique.  Clone your player module to play against yourself.')
            sys.exit(0)
        playerWins[player.strip()] = 0
   
    # play all pairings the players   
    while game <= MAX_GAMES:
        pairings = []
        for pairing in itertools.permutations(playerWins.keys(), 2):
            pairings.append(pairing)
        random.shuffle(pairings)
        for pairing in pairings:
            if game <= MAX_GAMES:
                play_game(pairing)
    
    # sort dictionary by wins and display rankings
    rank = 1
    for item in sorted(playerWins.items(), key=operator.itemgetter(1), reverse=True):
        print("Rank", rank, "is player", item[0], "with", item[1], "wins.")
        rank += 1
                
# plays a single game
def play_game(matchup):
    global game,  playerWins, PYTHON_PATH

    print ("Game: %s Matchup: %s" % (game, matchup))
    
    modules = [mod for mod in matchup]           
    res = str(subprocess.Popen([sys.executable,'quoridor.py','UI=False','ANIMATION_SPEED=%s' % (sys.argv[4] if len(sys.argv) > 4 else 500),'STDOUT_LOGGING=False','FILE_LOGGING=True','PLAYER_MODULES=%s'%','.join(modules), sys.argv[5] if (len(sys.argv) > 5) else 'config.txt'], stdout=subprocess.PIPE).communicate()[0])
       
    try:
        winningPlayer = [int(res.strip().split()[1]) - 1]
    except:
        if 'winner' in res:
            winningPlayer = []
        else:
            print ("Output was %s" % res.strip())
            print ("Parsing error occurred")
            winningPlayer = int(input("Enter winner id (1-2), 0 for no winner")) - 1
    
    try:    
        if winningPlayer != []:
            for p in winningPlayer:
                if p in (0,1):
                    playerWins[modules[p]] += 1
                    print ("\tWinner: %s" % (modules[p]))                      
        else:
            print ("\tNo winner.")
            
    except:
        print ("Input error")
        
    game += 1

if __name__ == "__main__":
    main()
    