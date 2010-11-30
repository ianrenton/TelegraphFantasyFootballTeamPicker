#!/usr/bin/python 
# -*- coding: cp1252 -*-
# Telegraph Fantasy Football Team Picker
# version 1.2.0 (12 August 2010)
# by Ian Renton and Mark Harris
# For details, see http://www.onlydreaming.net/software/telegraph-fantasy-football-team-picker
# This code is released under the GPLv3 licence (http://www.gnu.org/licenses/gpl.html).
# Takes player data from the TFF website, and picks the optimum team based
# on players' past performance and current injuries.

import re
import datetime

print "Content-Type: text/html\n\n"


# Port of MATLAB's nchoosek (unique combination) function.
def nchoosek(items, n):
    if n==0: yield []
    else:
        for (i, item) in enumerate(items):
            for cc in nchoosek(items[i+1:],n-1):
                yield [item]+cc

# Works out the position a given player number maps to.
def calculatePosition(number):
    if ((number < 2000) & (number >= 1000)):
        return "Goalkeeper"
    elif ((number < 3000) & (number >= 2000)):
        return "Defender"
    elif ((number < 4000) & (number >= 3000)):
        return "Midfielder"
    elif ((number < 5000) & (number >= 4000)):
        return "Striker"

def cutDownPlayerPointsHTML(html):
    goalkeepersStart = re.compile("<div class='pla-list' id='list-GK'><table>").search(html)
    goalkeepersEnd = re.compile("</table>").search(html[goalkeepersStart.start():len(html)])
    goalkeepersText = html[goalkeepersStart.start():goalkeepersStart.start()+goalkeepersEnd.end()]

    defendersStart = re.compile("<div class='pla-list' id='list-DEF'><table>").search(html)
    defendersEnd = re.compile("</table>").search(html[defendersStart.start():len(html)])
    defendersText = html[defendersStart.start():defendersStart.start()+defendersEnd.end()]

    midfieldersStart = re.compile("<div class='pla-list' id='list-MID'><table>").search(html)
    midfieldersEnd = re.compile("</table>").search(html[midfieldersStart.start():len(html)])
    midfieldersText = html[midfieldersStart.start():midfieldersStart.start()+midfieldersEnd.end()]

    strikersStart = re.compile("<div class='pla-list' id='list-STR'><table>").search(html)
    strikersEnd = re.compile("</table>").search(html[strikersStart.start():len(html)])
    strikersText = html[strikersStart.start():strikersStart.start()+strikersEnd.end()]

    return goalkeepersText + defendersText + midfieldersText + strikersText

def extractFields(text):
    textIndex = 0
    arrayIndex = 0
    interestingThings = []

    while textIndex < len(text):
        try:
            # Extract data between <tr> and </tr>.  This will get an individual player's line.
            startPos = re.compile("<tr\s?[^>]*>").search(text[textIndex:len(text)])
            endPos = re.compile("</tr>").search(text[textIndex+startPos.end():textIndex+startPos.start()+1000])
            thisItem = text[textIndex+startPos.start():textIndex+startPos.end()+endPos.end()]

            # Extract the ID field
            idStartPos = re.compile("id=\'p").search(thisItem)
            idEndPos = re.compile("\'").search(thisItem[idStartPos.end():len(thisItem)])
            interestingThings.append(thisItem[idStartPos.end():idStartPos.end()+idEndPos.end()-1])

            innerIndex = 0
            while innerIndex < len(thisItem):
                try:
                    # Extract data between <td> and </td>.  This will get the individual cells.
                    innerStartPos = re.compile("<td>").search(thisItem[innerIndex:len(thisItem)])
                    innerEndPos = re.compile("</td>").search(thisItem[innerIndex+innerStartPos.end():len(thisItem)])
                    innerItem = thisItem[innerIndex+innerStartPos.end():innerIndex+innerStartPos.end()+innerEndPos.start()]
                    innerIndex = innerIndex + innerStartPos.end() + innerEndPos.end()
                    interestingThings.append(innerItem)
                    arrayIndex += 1
                except:
                    break
                
            textIndex = textIndex+startPos.end()+endPos.end()
        except:
            break
        
    return interestingThings

class Player:
    def __init__(self, row):
        self.number = int(row[0])
        self.name = row[1]
        self.team = row[2]
        self.points = int(row[3])
        self.price = round(float(row[4]), 1)
        self.value = self.points / self.price
        self.position = calculatePosition(self.number)
        
    def __str__(self):
        return '<tr><td><p>%4s</p></td><td><p>%-20s</p></td><td><p>%-20s</p></td><td><p>%4s</p></td><td><p>%4s</p></td></tr>' % (self.number, self.name, self.team, self.price, self.points)

class TeamPicker:
    def __init__(self):
        self.process()
        
    def set_initial_text(self):
        # Print header
        introText = "<h2>Optimum Telegraph Fantasy Football Team</h2><p style=\"font-weight:bold\">Generated on " + datetime.datetime.now().strftime("%A %d %B %Y at %H:%M:%S.") + "</p>"
        introText = introText + "<p>Created using Telegraph Fantasy Football Team Picker, version 1.2.0 (12 August 2010), by Ian Renton and Mark Harris.<br>"
        introText = introText + "For details and source code, see <a href=\"http://www.onlydreaming.net/software/telegraph-fantasy-football-team-picker\">http://www.onlydreaming.net/software/telegraph-fantasy-football-team-picker</a></p>"
        self.displayUpdate(introText)

    def displayUpdate(self, line):
        self.f.write(line)

    def process(self):
        import urllib2
        import re

        from collections import defaultdict

        try:
            urllib2.urlopen('http://www.google.com')
        except urllib2.URLError, e:
            self.f = open('./output.html', 'w')	
            self.set_initial_text()
            self.displayUpdate('<p style="font-weight:bold">Internet connection failed.</p>')
            internetConnectionAvailable = False
        else:
            internetConnectionAvailable = True

        if internetConnectionAvailable == True:
            
            # Download the HTML file, and create a 'tmpData' list to contain the information.
            try:
                response = urllib2.urlopen('http://fantasyfootball.telegraph.co.uk/select-team/')
                html = response.read()
            except IOError, e:
                self.f = open('./output.html', 'w')	
                self.set_initial_text()
                self.displayUpdate('<p style="font-weight:bold">Could not find the player list, maybe the URL has changed?</p>')
                return
            else:
                pass
        else:
            self.f = open('./output.html', 'w')	
            self.set_initial_text()
            self.displayUpdate('<p style="font-weight:bold">Using a local mirror of the player list.</p>')
            
            # Load the HTML file, and create a 'tmpData' list to contain the information.
            try:
                tmpFile = open("export.html","r")
                html = tmpFile.read()
                tmpFile.close()
            except IOError, e:
       	        self.f = open('./output.html', 'w')	
                self.set_initial_text()
                self.displayUpdate('<p style="font-weight:bold">Cannot continue.</p>')
                return
            else:
                pass

        # Process the HTML into Players
        fields = extractFields(cutDownPlayerPointsHTML(html))
        tmpData = []
        for i in range(len(fields)/7):
            # If Points field is blank, replace it with a zero.
            if (fields[i*7+5] == ""):
                fields[i*7+5] = 0
            # Add player (ID, name, club, points, price)
            tmpData.append(Player([fields[i*7],fields[i*7+1],fields[i*7+2],fields[i*7+5],fields[i*7+3]]))

        # Extra features if we have a net connection
        if internetConnectionAvailable == True:

            # Fetch injury list from PhysioRoom
            response = urllib2.urlopen('http://www.physioroom.com/news/english_premier_league/epl_injury_table.php')
            injuryList = response.read()

            # Remove injured players
            tmpData = filter(lambda player : re.compile(player.name).search(injuryList)==None, tmpData)
            
            # Fetch transfer password from RichardSweeting.org
            response = urllib2.urlopen('http://www.richardsweeting.org/pages/telegraph.html')
            passwordPage = response.read()

            # Find the Wednesday's date and the password.
            try:
                match = re.compile("<p style=\"padding-top: 0pt; \" class=\"paragraph_style_1\">[^\n]*\n").search(passwordPage)
                match2 = re.compile("[^<]*<").search(passwordPage[match.start()+56:match.end()])
                wednesday = passwordPage[match.start()+56:match.start()+56+match2.end()-1]
            except:
                wednesday = "???"
                
            try:
                match = re.compile("\*\*\* [A-Za-z]* \*\*\*").search(passwordPage)
                password = passwordPage[match.start()+4:match.end()-4]
            except:
                password = "Unknown  (Could not parse page, visit <a href=\"http://www.richardsweeting.org/pages/telegraph.html\">http://www.richardsweeting.org/pages/telegraph.html</a> to check manually.)"

            transferPasswordInfo = "<p>Transfer password for %s: %s</p>" % (wednesday, password)
        else:
            pass

        # Split data into four separate lists, one for each kind of player.
        players = defaultdict(list)
        for player in tmpData:
            players[player.position].append(player)

        # Produce a set of thresholds for VFM and overall price.  This allows us to cut
        # down the list of players to only those that are good value for money or
        # particularly high-scoring.  This mirrors human behaviour, where the user
        # picks some very high-scoring (but expensive) players, then fills out the rest
        # of the team with cheap but good-value players.
        # These thresholds are necessary to reduce the number of players being considered,
        # as otherwise the number of combinations that the script must consider would be
        # too large for the script to run in sensible time.

        thresholdDivisor = 1.6
        sensibleDataSet = 0
        while (sensibleDataSet == 0):
            points = lambda player: player.points
            valueForMoney = lambda player: player.value

            pointThresholds = defaultdict(float)
            valueThresholds = defaultdict(float)
            for position in players.keys():
                pointThresholds[position] = max(players[position], key=points).points / thresholdDivisor
                valueThresholds[position] = max(players[position], key=valueForMoney).value / thresholdDivisor

            # This section applies the thresholds calculated in the previous one, to cut down
            # the number of players.
            for position in players.keys():
                players[position] = filter(lambda x : ((x.points > pointThresholds[position]) | (x.value > valueThresholds[position])), players[position])

            # Using a function to pick unique combinations of players, we here form a list of
            # all possible combinations: 1 2 3 4, 1 2 3 5, 1 2 3 6 and so on.  Because there
            # are multiple formations to choose from, we have to do this several times.
            defenderChoices3 = list(nchoosek(players["Defender"],3))
            defenderChoices4 = list(nchoosek(players["Defender"],4))

            # Now the same for the midfielders.
            midfielderChoices3 = list(nchoosek(players["Midfielder"],3))
            midfielderChoices4 = list(nchoosek(players["Midfielder"],4))
            midfielderChoices5 = list(nchoosek(players["Midfielder"],5))

            # And now the same for the strikers.
            strikerChoices1 = list(nchoosek(players["Striker"],1))
            strikerChoices2 = list(nchoosek(players["Striker"],2))
            strikerChoices3 = list(nchoosek(players["Striker"],3))

            # To reduce the number of combinations, we just pick the one goalkeeper
            # who provides best value for money rather than searching through them all.
            players["Goalkeeper"].sort(lambda x, y: cmp(y.value, x.value))
            goalkeeper = players["Goalkeeper"][0]

            # For each combination of defenders, we calculate their combined price
            # and combined points totals.

            # Create two functions that, given a list of permutations of players, will return a list of prices of those players in the same order.
            # Er... I guess if you're not up on your functional programming, this must look a bit hideous...
            prices = lambda permutations: reduce(lambda total, player: total + player.price, permutations, 0)
            points = lambda permutations: reduce(lambda total, player: total + player.points, permutations, 0)
            #Sorry! Having those simplifies the next bit dramatically though:
            defChoicesPrice3 = map(prices, defenderChoices3)
            defChoicesPoints3 = map(points, defenderChoices3)
            defChoicesPrice4 = map(prices, defenderChoices4)
            defChoicesPoints4 = map(points, defenderChoices4)

            # Same for the midfielders.
            midChoicesPrice3 = map(prices, midfielderChoices3)
            midChoicesPoints3 = map(points, midfielderChoices3)            
            midChoicesPrice4 = map(prices, midfielderChoices4)
            midChoicesPoints4 = map(points, midfielderChoices4)            
            midChoicesPrice5 = map(prices, midfielderChoices5)
            midChoicesPoints5 = map(points, midfielderChoices5)

            # Same for the strikers.
            strChoicesPrice1 = map(prices, strikerChoices1)
            strChoicesPoints1 = map(points, strikerChoices1)            
            strChoicesPrice2 = map(prices, strikerChoices2)
            strChoicesPoints2 = map(points, strikerChoices2)         
            strChoicesPrice3 = map(prices, strikerChoices3)
            strChoicesPoints3 = map(points, strikerChoices3)

            # If we have too many iterations to be possible in sensible time, go back and reduce
            # thresholdDivisor until we have something sensible.  Assume the 442 formation is pretty representative.
            totalIterations = len(defenderChoices4) * len(midfielderChoices4) * len(strikerChoices2)
            print thresholdDivisor
            print totalIterations
            if (totalIterations <= 15000000):
                sensibleDataSet = 1
            else:
                thresholdDivisor = thresholdDivisor - 0.05
            
        # Now we iterate through all possible choices for defenders, midfielders and
        # strikers.  In each case, we check to see if this set is better than the one
        # before, and if so we record it.  First, the 442 team.
        bestTotalPoints = 0
        bestChoices = []
        bestFormation = 0
        maxPrice = 50 - goalkeeper.price

        # 442
        for (i, defs) in enumerate(defenderChoices4):
            for (j, mids) in enumerate(midfielderChoices4):
                for (k, strs) in enumerate(strikerChoices2):
                    if ((defChoicesPrice4[i] + midChoicesPrice4[j] + strChoicesPrice2[k]) <= maxPrice):
                        teamPoints = (defChoicesPoints4[i] + midChoicesPoints4[j] + strChoicesPoints2[k])
                        if (teamPoints > bestTotalPoints):
                            bestTotalPoints = teamPoints
                            (bestDefs, bestMids, bestStrs) = (defs, mids, strs)

        # 433
        for (i, defs) in enumerate(defenderChoices4):
            for (j, mids) in enumerate(midfielderChoices3):
                for (k, strs) in enumerate(strikerChoices3):
                    if ((defChoicesPrice4[i] + midChoicesPrice3[j] + strChoicesPrice3[k]) <= maxPrice):
                        teamPoints = defChoicesPoints4[i] + midChoicesPoints3[j] + strChoicesPoints3[k]
                        if (teamPoints > bestTotalPoints):
                            bestTotalPoints = teamPoints
                            (bestDefs, bestMids, bestStrs) = (defs, mids, strs)

        # 451
        for (i, defs) in enumerate(defenderChoices4):
            for (j, mids) in enumerate(midfielderChoices5):
                for (k, strs) in enumerate(strikerChoices1):
                    if ((defChoicesPrice4[i] + midChoicesPrice5[j] + strChoicesPrice1[k]) <= maxPrice):
                        teamPoints = defChoicesPoints4[i] + midChoicesPoints5[j] + strChoicesPoints1[k]
                        if (teamPoints > bestTotalPoints):
                            bestTotalPoints = teamPoints
                            (bestDefs, bestMids, bestStrs) = (defs, mids, strs)

        # 352
        for (i, defs) in enumerate(defenderChoices3):
            for (j, mids) in enumerate(midfielderChoices5):
                for (k, strs) in enumerate(strikerChoices2):
                    if ((defChoicesPrice3[i] + midChoicesPrice5[j] + strChoicesPrice2[k]) <= maxPrice):
                        teamPoints = defChoicesPoints3[i] + midChoicesPoints5[j] + strChoicesPoints2[k]
                        if (teamPoints > bestTotalPoints):
                            bestTotalPoints = teamPoints
                            (bestDefs, bestMids, bestStrs) = (defs, mids, strs)

        # Calculate optimum team's total price.
        bestTotalPrice = goalkeeper.price
        for p in bestDefs:
            bestTotalPrice += p.price
        for p in bestMids:
            bestTotalPrice += p.price
        for p in bestStrs:
            bestTotalPrice += p.price

        # Print the optimum team's details.
        self.f = open('./output.html', 'w')	
        self.set_initial_text()
        self.displayUpdate('<table width="500px" border="1" cellspacing="2">')
        self.displayUpdate('<tr><td><p><b>ID</b></p></td><td><p><b>Name</b></p></td><td><p><b>Club</b></p></td><td><p><b>Price</b></p></td><td><p><b>Points</b></p></td></tr>')
        self.displayUpdate('<tr><td colspan=5><p><b>Goalkeeper</b></p></td></tr>')
        self.displayUpdate( str(goalkeeper))
        self.displayUpdate('<tr><td colspan=5><p><b>Defenders</b></p></td></tr>')
        self.displayUpdate( ''.join(map(str, bestDefs)))
        self.displayUpdate('<tr><td colspan=5><p><b>Midfielders</b></p></td></tr>')
        self.displayUpdate(''.join(map(str, bestMids)))
        self.displayUpdate('<tr><td colspan=5><p><b>Strikers</b></p></td></tr>')
        self.displayUpdate(''.join(map(str, bestStrs)))
        self.displayUpdate('<tr><td colspan=3><p><b>Total</b></p></td><td><p><b>%4s</b></p></td><td><p><b>%4s</b></p></td></tr>' % (bestTotalPrice, bestTotalPoints))
        self.displayUpdate('</table>')
        
        self.displayUpdate(transferPasswordInfo)

        self.f.close()
        print "<p><a href=\"output.html\">output.html</a> successfully generated.</p>"
        return 0

teampicker = TeamPicker()
