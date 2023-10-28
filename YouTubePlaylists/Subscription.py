from prettytable import PrettyTable

class Subscription:
    week = {
        "monday" : 0,
        "tuesday" : 1,
        "wednesday" : 2,
        "thursday" : 3,
        "friday" : 4,
        "saturday" : 5,
        "sunday" : 6
    }   

    def __init__(self, username, channelID, playlist, allowLive, allowShorts):
        self.username = username
        self.channelID = channelID
        self.playlist = playlist
        self.restrictions = {
            "include" : [],
            "exclude" : [],
            "date" : []
        }
        self.allowLive = allowLive
        self.allowShorts = allowShorts

    # Attach more restrictions to the Subscription 
    def addMoreRestrictions(self):
        myTable = PrettyTable(["Restrictions"])
        for restriction in self.listRestrictions():
            myTable.add_row([restriction])

        print(myTable)

        return self.addRestrictions()

    # Attach restrictions to the Subscription
    def addRestrictions(self):
        restrictionList = self.restriction()
        if not restrictionList:
            return False

        restrictionsDict = self.deligateRestrictions(restrictionList)
        if not restrictionsDict:
            return self.addRestrictions()
        self.restrictions = restrictionsDict
        return restrictionsDict


    # Get numeric value from day of the week
    def dateConversion(self, date):
        try:
            return self.week[date]
        except:
            print(f"\nIncorrect date value ({date})\n")
            return "cancel"
    
    # Convert list to dictionary of restrictions
    def deligateRestrictions(self, restrictionList):
        for restriction in restrictionList:
            if restriction == '':
                continue;
            if restriction[0] == '!':
                self.restrictions["exclude"].append(restriction[1:])
            elif restriction.lower().startswith("date:"):
                numericDate = self.dateConversion(restriction[5:].lower())
                if numericDate == "cancel":
                    return False
                self.restrictions["date"].append(numericDate)
            else:
                self.restrictions["include"].append(restriction)

        self.sortRestrictions()

        return self.restrictions

    # Convert restrictions dictionary to a list
    def listRestrictions(self):
        restrictionsList = []

        restrictionsList += self.restrictions["include"]
        for exclude in self.restrictions["exclude"]:
            restrictionsList.append('!' + exclude)
        for date in self.restrictions["date"]:
            restrictionsList.append("date:" + list(self.week.keys())[date])
        if len(restrictionsList) == 0:
            restrictionsList.append('')
        return restrictionsList

    # Obtain a list of restriction associated with the channel
    def restriction(self):
        print("""Restrictions are separated by ','s. '!' is used to not include that selection. 
            'date:' is used to include videos published on that day of the week""")
        allRestrictions = input("Enter any restrictions (Enter cancel to leave): ")

        if allRestrictions == "cancel":
            return False
        restrictionsList = allRestrictions.split(",")
        for i in range(len(restrictionsList)):
            restrictionsList[i] = restrictionsList[i].strip()
        return restrictionsList

    # Sort the lists within restrictions
    def sortRestrictions(self):
        self.restrictions["include"].sort()
        self.restrictions["exclude"].sort()
        self.restrictions["date"].sort()