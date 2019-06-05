class Level:
    def __init__(self, levelName='Full'):
        self.buildLevelDict()
        try:
            self.string_representation = self.levelDict[levelName]
        except KeyError:
            self.string_representation = self.levelDict['Full']
            print("Level name not found, defaulting to full level.")
    
    def buildLevelDict(self):    
        self.levelDict = dict()
        # Empty Field
        self.levelDict['Empty'] = [
            "PPPPPPPPPPPPPPPPPPPP",
            "P                  P",
            "P                  P",
            "P                  P",
            "P                  P",
            "P                  P",
            "P                  P",
            "P                  P",
            "P                  P",
            "P                  P",
            "P                  P",
            "P                  P",
            "P                  P",
            "P                  P",
            "P                  P",
            "P                  P",
            "P                  P",
            "PPPPPPPPPPPPPPPPPPPP", ]

        # Race Track
        self.levelDict['Race'] = [
            "PPPPPPPPPPPPPPPPPPPP",
            "PPPPPPPPPPPPPPPPPPPP",
            "PPPPPPPPPPPPPPPPPPPP",
            "PPP PPPPPPPPPPPPPPPP",
            "PPP PPPPPPPPPPPPPPPP",
            "PPP PPPPPPPPPPPPPPPP",
            "PPP PPPPPPPPPPPPPPPP",
            "PPP PPPPPPPPPPPPPPPP",
            "PPP PPPPPPPPPPPPPPPP",
            "PPP PPPPPPPPPPPPPPPP",
            "PPP PPPPPPPPPPPPPPPP",
            "PPP PPPPPPPPPPPPPPPP",
            "PPP PPPPPPPPPPPPPPPP",
            "PPP PPPPPPPPPPPPPPPP",
            "PPP PPPPPPPPPPPPPPPP",
            "PPP PPPPPPPPPPPPPPPP",
            "PPP PPPPPPPPPPPPPPPP",
            "PPPPPPPPPPPPPPPPPPPP", ]

        # Race Track 2
        self.levelDict['Race2'] = [
            "PPPPPPPPPPPPPPPPPPPP",
            "PPPPPPPPPPPPPPPPPPPP",
            "PP                PP",
            "PP PPPPPPPPPPPPPP PP",
            "PP PPPPPPPPPPPPPP PP",
            "PP PPPPPPPPPPPPPP PP",
            "PP PPPPPPPPPPPPPP PP",
            "PP PPPPPPPPPPPPPP PP",
            "PP PPPPPPPPPPPPPP PP",
            "PP PPPPPPPPPPPPPP PP",
            "PP PPPPPPPPPPPPPP PP",
            "PP PPPPPPPPPPPPPP PP",
            "PP PPPPPPPPPPPPPP PP",
            "PP PPPPPPPPPPPPPP PP",
            "PP PPPPPPPPPPPPPP PP",
            "PP                PP",
            "PPPPPPPPPPPPPPPPPPPP",
            "PPPPPPPPPPPPPPPPPPPP", ]

        # Randomness
        self.levelDict['Chaos'] = [
            "PPPPPPPPPPPPPPPPPPPP",
            "P                  P",
            "P        P PP PPP  P",
            "P         P  PPPP  P",
            "P         P   PPP  P",
            "P                  P",
            "P  P   PPPPPP   P  P",
            "P  P   P    P   P  P",
            "P  P   P    P   P  P",
            "P  P   PP  PP   P  P",
            "P                  P",
            "PPP    P P         P",
            "PPP P    PP P  P   P",
            "PPP PP   PP P  P   P",
            "PPP  PPPPPP PPP    P",
            "PPPP        PPP    P",
            "PPPP        PPP    P",
            "PPPPPPPPPPPPPPPPPPPP", ]

        # Full Level
        self.levelDict['Full'] = [
            "PPPPPPPPPPPPPPPPPPPP",
            "PPPPPPPPPPPPPPPPPPPP",
            "P                  P",
            "P   PPPPP  PPPPPP  P",
            "P                  P",
            "P  P PPPPPPPPPP P  P",
            "P  P            P  P",
            "P  P P PPPPPP P P  P",
            "P    P P    P P    P",
            "P    P P    P P    P",
            "P  P P PP  PP P P  P",
            "P  P            P  P",
            "P  P PPPPPPPPPP P  P",
            "P                  P",
            "P  PPPPPP  PPPPPP  P",
            "P                  P",
            "PPPPPPPPPPPPPPPPPPPP",
            "PPPPPPPPPPPPPPPPPPPP", ]

        # Full Level - Single Tracks Only
        self.levelDict['FullSingle'] = [
            "PPPPPPPPPPPPPPPPPPPP",
            "PPPPPPPPPPPPPPPPPPPP",
            "PP                PP",
            "PP PPPPPP PPPPPPP PP",
            "PP                PP",
            "PP P PPPPPPPPPP P PP",
            "PP P            P PP",
            "PP P P PPPPPP P P PP",
            "PP   P PXXXXP P P PP",
            "PP P P PXXXXP P   PP",
            "PP P P PPXXPP P P PP",
            "PP P            P PP",
            "PP P PPPPPPPPPP P PP",
            "PP                PP",
            "PP PPPPPPP PPPPPP PP",
            "PP                PP",
            "PPPPPPPPPPPPPPPPPPPP",
            "PPPPPPPPPPPPPPPPPPPP", ]