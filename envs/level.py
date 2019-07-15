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

        self.levelDict['RaceGhost'] = [
            "PPPPPPPPPPPPPPPPPPPP",
            "PPPPPPPPPPPPPPPPPPPP",
            "PP                PP",
            "PP PPPPP PP PPPPP PP",
            "PP PPPPP PP PPPPP PP",
            "PP PPPPP PP PPPPP PP",
            "PP PPPPP PP PPPPP PP",
            "PP PPPPP PP PPPPP PP",
            "PP PPPPPXPPXPPPPP PP",
            "PP PPPPP PP PPPPP PP",
            "PP PPPPP PP PPPPP PP",
            "PP PPPPP PP PPPPP PP",
            "PP PPPPP PP PPPPP PP",
            "PP PPPPP PP PPPPP PP",
            "PP PPPPP PP PPPPP PP",
            "PP                PP",
            "PPPPPPPPPPPPPPPPPPPP",
            "PPPPPPPPPPPPPPPPPPPP", ]

        self.levelDict['RaceGhostX'] = [
            "PPPPPPPPPPPPPPPPPPPP",
            "PPPPPPPPPPPPPPPPPPPP",
            "PP                PP",
            "PP PPPPPXPP PPPPP PP",
            "PP PPPPPXPP PPPPP PP",
            "PP PPPPPXPP PPPPP PP",
            "PP PPPPPXPP PPPPP PP",
            "PP PPPPPXPP PPPPP PP",
            "PP PPPPPXPPXPPPPP PP",
            "PP PPPPPXPP PPPPP PP",
            "PP PPPPPXPP PPPPP PP",
            "PP PPPPPXPP PPPPP PP",
            "PP PPPPPXPP PPPPP PP",
            "PP PPPPPXPP PPPPP PP",
            "PP PPPPPXPP PPPPP PP",
            "PP                PP",
            "PPPPPPPPPPPPPPPPPPPP",
            "PPPPPPPPPPPPPPPPPPPP", ]
        
        self.levelDict['AvoidGhost'] = [
            "PPPPPPPPPPPPPPPPPPPP",
            "PPPPPPPPPPPPPPPPPPPP",
            "PPP      PPPPPPPPPPP",
            "PPPPPPPP PPPPPPPPPPP",
            "PPPPPPPP PPPPPPPPPPP",
            "PPPPPPPP PPPPPPPPPPP",
            "PPPPPPPP PPPPPPPPPPP",
            "PPPPPPPP    PPPPPPPP",
            "PPPPPPPPXPP PPPPPPPP",
            "PPPPPPPP    PPPPPPPP",
            "PPPPPPPP PPPPPPPPPPP",
            "PPPPPPPP PPPPPPPPPPP",
            "PPPPPPPP PPPPPPPPPPP",
            "PPPPPPPP PPPPPPPPPPP",
            "PPPPPPPP PPPPPPPPPPP",
            "PPPPPPPP         PPP",
            "PPPPPPPPPPPPPPPPPPPP",
            "PPPPPPPPPPPPPPPPPPPP", ]

        self.levelDict['Wide'] = [
            "PPPPPPPPPPPPPPPPPPPP",
            "PPPPPPPPPPPPPPPPPPPP",
            "P     P PP    P    P",
            "P PPPPP PP PP P PPPP",
            "P   PPP PP    P    P",
            "P PPPPP PP PP PPPP P",
            "P PPPPP PP PP P    P",
            "P                  P",
            "P PPPPPPXPPXPPPPPP P",
            "P PPPPPP PP PPPPPP P",
            "P                  P",
            "P PPPPP PP PP P    P",
            "P PPPPP PP PP PPPP P",
            "P   PPP PP    P    P",
            "P PPPPP PP PP P PPPP",
            "P     P PP    P    P",
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
            "P  P   PXXXXP   P  P",
            "P  P   PXXXXP   P  P",
            "P  P   PPXXPP   P  P",
            "P                  P",
            "PPP    P P         P",
            "PPP P    PP P  P   P",
            "PPP PP   PP P  P   P",
            "PPP  PPPPPP PPP    P",
            "PPPP        PPP    P",
            "PPPPPPPPPPP PPPPPPPP",
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
            "P    P PXXXXP P    P",
            "P    P PXXXXP P    P",
            "P  P P PPXXPP P P  P",
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
            "PP P P PXXXXP P P PP",
            "PP   P PXXXXP P P PP",
            "PP P P PXXXXP P   PP",
            "PP P P PXXXXP P P PP",
            "PP P            P PP",
            "PP P PPPPPPPPPP P PP",
            "PP                PP",
            "PP PPPPPPP PPPPPP PP",
            "PP                PP",
            "PPPPPPPPPPPPPPPPPPPP",
            "PPPPPPPPPPPPPPPPPPPP", ]
        
        self.levelDict['MsPacman'] = [
            "PPPPPPPPPPPPPPPPPPPP",
            "P     P      P     P",
            "P PPP P PPPP P PPP P",
            "P                  P",
            "PP P PPPXPPXPPP P PP",
            "PP P PPPXPPXPPP P PP",
            "PP P  XXXXXXXX  P PP",
            "PP PP PPXXXXPP PP PP",
            "PP PP PPXXXXPP PP PP",
            "PP    PPXXXXPP    PP",
            "PP P PPPXXXXPPP P PP",
            "PP P XXXXXXXXXX P PP",
            "PP P PPPXPPXPPP P PP",
            "PP P PPPXPPXPPP P PP",
            "P                  P",
            "P PPP P PPPP P PPP P",
            "P     P      P     P",
            "PPPPPPPPPPPPPPPPPPPP", ]