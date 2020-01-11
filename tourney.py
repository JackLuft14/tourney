# Tool for updating Smash tournaments
import time
from selenium import webdriver
from pushbullet import Pushbullet

test = True

# read access
f = open("access.txt","r")
push = f.read()
f.close()
push = push[:len(push)-1]


pb = Pushbullet(push)

driver = webdriver.Firefox()

#TODO
tourney = "The Mang0"
url = "https://smash.gg/tournament/mango-s-birthday-bash-red-bull-adrenalan/events/melee-singles/brackets/711519/1151656"

GF = "Grand Finals"
WF = "Winners Finals"
WS = "Winners Semis"
WQ = "Winners Quarters"
LF = "Losers Finals"
LS = "Losers Semis"
LQ = "Losers Quarters"
LE = "Losers Eighths"
LX = "Losers Sixteenths"
LL = "Losers 1"

top6  = [WS,WS,WF,GF,GF,LQ,LQ,LS,LF]
top8  = [WS,WS,WF,GF,GF,LE,LE,LQ,LQ,LS,LF]
top12 = [WS,WS,WF,GF,GF,LX,LX,LX,LX,LE,LE,LQ,LQ,LS,LF]
top13 = [WQ,WQ,WQ,WQ,WS,WS,WF,GF,GF,LX,LX,LX,LX,LE,LE,LQ,LQ,LS,LF]
top16 = [WQ,WQ,WQ,WQ,WS,WS,WF,GF,GF,LL,LL,LL,LL,LX,LX,LX,LX,LE,LE,LQ,LQ,LS,LF]
top = top6

class Match:
    def __init__(self,text):
        fields = text.split('\n')
        self.letter = fields[len(fields)-1]
        self.round = top[ord(self.letter)-65]
        if len(fields) == 5:
            self.player1 = fields[0]
            self.player2 = fields[2]
            self.score1 = int(fields[1])
            self.score2 = int(fields[3])
        else:
            self.player1 = "..."
            self.player2 = "..."
            self.score1 = -1
            self.score2 = -1

        for i in range(len(self.player1)):
            if ord(self.player1[i]) > 126:
                self.player1 = self.player1[:i] + '.' + self.player1[i+1:]

        for i in range(len(self.player2)):
            if ord(self.player2[i]) > 126:
                self.player2 = self.player2[:i] + '.' + self.player2[i+1:]

    def printMatch(self):
        astring  = str(self.score1) + " " + self.player1 + "\n"
        astring += str(self.score2) + " " + self.player2 + "\n"
        astring += self.round
        print(astring)
        return astring

    def update(self,newMatch):
        self.player1 = newMatch.player1
        self.player2 = newMatch.player2
        self.score1  = newMatch.score1
        self.score2  = newMatch.score2

    def equal(self,newMatch):
        if self.player1 == newMatch.player1:
            if self.player2 == newMatch.player2:
                if self.score1 == newMatch.score1:
                    if self.score2 == newMatch.score2:
                        return True
        return False

def notifyMe(aMatch):
    print("UPDATE")
    pb.push_note(aMatch.printMatch(),tourney)


###### MAIN ######

driver.get(url)

matchHTML = driver.find_elements_by_class_name('match-affix-wrapper')

# count matches (account for GF set 2)
if len(matchHTML) == len(top6)-1 or len(matchHTML) == len(top6):
    top = top6
elif len(matchHTML) == len(top8)-1 or len(matchHTML) == len(top8):
    top = top8
elif len(matchHTML) == len(top12)-1 or len(matchHTML) == len(top12):
    top = top12
elif len(matchHTML) == len(top13)-1 or len(matchHTML) == len(top13):
    top = top13
elif len(matchHTML) == len(top16)-1 or len(matchHTML) == len(top16):
    top = top16
else:
    print("ERROR: Incorrect number of matches")
    notifyMe(Match("ERROR\n0\nNum matches\n0\nA"))

extra = False
if len(matchHTML)%2 == 0: #need to add placeholder for GF2
    extra = True

# running list of all matches
matches = []

i = 0
for match in matchHTML:
    aMatch = Match(match.text)
    if extra: #add temp match for GF2
        if i > 0 and ord(aMatch.letter) == ord(matches[len(matches)-1].letter)+2:
            matches.append(Match("GF\n0\nSet2\n0\n"+str(chr(ord(aMatch.letter)-1))))
            extra = False
        i += 1
    matches.append(aMatch)

# loop continuously to check for updates
if not test:
    count = 0
    while count < 6:
        timer.sleep(600) # 10 minutes
        i = 0
        driver.get(url)

        matchHTML = driver.find_elements_by_class_name('match-affix-wrapper')

        for match in matchHTML:
            aMatch = Match(match.text)

            # move on if no GF2
            if top[i] == GF and top[i-1] == GF:
                i += 1

            # if an update occurs, send notification
            if matches[i].equal(aMatch) == False:
                matches[i].update(aMatch)
                notifyMe(aMatch)
                count = -1

            i += 1
        #end for
        count += 1
    #end while
else:
    i = 0
    driver.get(url)

    matchHTML = driver.find_elements_by_class_name('match-affix-wrapper')

    tempvar = "NAN"
    for match in matchHTML:
        if i == 5: #force update
            tempset = match.text.split('\n')[4]
            tempvar = "Noelle\n5\nJack\n4\n" + tempset
        else:
            tempvar = match.text
        aMatch = Match(tempvar)

        # move on if no GF2
        if top[i] == GF and top[i-1] == GF:
            i += 1

        # if an update occurs, send notification
        if matches[i].equal(aMatch) == False:
            matches[i].update(aMatch)
            notifyMe(aMatch)

        i += 1
    #end for
#end if

if not test:
    notifyMe(Match("DONE\n0\nExiting\n0\nA"))

driver.quit()
