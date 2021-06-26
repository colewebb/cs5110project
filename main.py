import json
import os

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

    def utility(self):
        pass

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
        print(limit[i])
    
    #set initial matchups
    for user in req['users']:
        #start at their available start
        start = user['availableStart']
        end = user['availableEnd']
        minSpace = user['space']
        minComp = user['computer']
        current = start

        print(user['name'])

        if limit[current]['spaces'][minSpace] > 0 and limit[current]['computers'][minComp] > 0:
            limit[current]['spaces'][minSpace] = limit[current]['spaces'][minSpace] - 1
            limit[current]['computers'][minComp] = limit[current]['computers'][minComp] -1
            limit[current]['users'] = limit[current]['users'].append(user['name'])
        
    for i in range(space['globals']['buildingClosedEnd'], 25):
        print(i, limit[i])
        



if __name__ == "__main__":
    # requirementsLocation = input(" Requirements location >>> ")
    # spaceLocation = input(" Space location >>> ")
    here = os.path.dirname(os.path.abspath(__file__))
    requirementsLocation = open(os.path.join(here, "test1Requirements.json"),"r")
    spaceLocation = open(os.path.join(here, "test1Space.json"),"r")

    pO = projectOpen(requirementsLocation, spaceLocation)
    pO.main()