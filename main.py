import json
import enum
import os

class Size(enum.Enum):
    small = 1
    medium = 2
    large = 3

    thin = 1
    powerful = 3

class projectOpen():
    def __init__(self, requirements, space):
        reqExists = False
        spExists = False
        try:
            self.req = json.load(requirements)
            reqExists = True
        except:
            reqExists = False
        try:
            self.sp = json.load(space)
            spExists = True
        except:
            spExists = False
        if not reqExists and not spExists:
            print("This program requires either just a set of requirements, or a set of requirements and a set of space.")
            print("Please confirm that the files you entered exist and try again.")
            exit(1)
        elif not spExists:
            print("Assuming infinite space. Generating perfect configuration...")
        elif spExists and reqExists:
            print("Building schedule for the given space and requirements constraints....")
            dataFusion(self.req, self.sp)
        else:
            print("Error 1")
            exit(1)

    def main(self):
        print()
        # print(self.req)
        # print(self.sp)

def dataFusion(req, space):
    #set up limits
    limit = {}
    for i in range (space['globals']['buildingClosedEnd'], 25):
        limit[i] = {
            'computers': space['computers'].copy(),
            'spaces': space['spaces'].copy(),
            'users': []
        }
    
    #set initial matchups
    notFound = []
    for user in req['users']:
        #start at their available start
        start = user['availableStart']
        end = user['availableEnd']
        hours = user['hoursNeeded']
        minSpace = user['space']
        minComp = user['computer']
        found = False

        # test = user['space']

        # print(test)
        # print(Size[test].value)

        #if there is a computer and space that exactly matches their conditions
        for i in range(start, end-hours):
            # print(i,limit[i]['spaces']['count'],limit[i]['computers']['count'])
            if limit[i]['spaces']['count'][minSpace] > 0 and limit[i]['computers']['count'][minComp] > 0:
                found = True
                #check to make sure they are available for the entire time they need to work
                for x in range(1,hours):
                    if not limit[i+x]['spaces']['count'][minSpace] > 0 and not limit[i+x]['computers']['count'][minComp] > 0:
                        found = False
                #if they are, then break
                if found:
                    current = i
                    break

        #if there is, give it to them
        # if found:
        #     print("found at", current)
        #     for x in range(0,hours):
        #         print(x)
        #         limit[current+x]['spaces']['count'][minSpace] = limit[current+x]['spaces']['count'][minSpace] - 1
        #         limit[current+x]['computers']['count'][minComp] = limit[current+x]['computers']['count'][minComp] -1
        #         limit[current+x]['users'].append(user['name'])
        # else:
        #     print("could not find suitable place for", user['name'])
    # printSchedule(limit)
        
def printSchedule(limit):
    # print(limit)
    for i in range(4,24):
        print(i, limit[i]['users'])
        


if __name__ == "__main__":
    # requirementsLocation = input(" Requirements location >>> ")
    # spaceLocation = input(" Space location >>> ")
    here = os.path.dirname(os.path.abspath(__file__))
    requirementsLocation = open(os.path.join(here, "test1Requirements.json"),"r")
    spaceLocation = open(os.path.join(here, "test1Space.json"),"r")

    pO = projectOpen(requirementsLocation, spaceLocation)
    pO.main()