import random
import json
import enum
import copy
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
            initial = dataFusion(self.req, self.sp)
            genetic(initial, self.req)

        else:
            print("Error 1")
            exit(1)


    def utility(self, user, startTime, endTime, computer, space):
        utilitySoFar = 0
        data = None
        for u in self.req['users']:
            if u['name'] == user:
                data = u
        if data == None:
            raise ArithmeticError
        # +- 100 if startTime, endTime in availableTime
        if startTime >= data['availableStart'] and endTime <= data['availableEnd']:
            utilitySoFar += 100
        else:
            utilitySoFar -= 100
        # +- 100 if computational needs met
        if self.sp['computers']['ranking'][computer] >= self.sp['computers']['ranking'][data['computer']]:
            utilitySoFar += 100
        else:
            utilitySoFar -= 100
        # +- 50 if space needs met
        if self.sp['spaces']['ranking'][space] >= self.sp['spaces']['ranking'][data['space']]:
            utilitySoFar += 50
        else:
            utilitySoFar -= 50
        # + 10 if extra computational power
        if self.sp['computers']['ranking'][computer] > self.sp['computers']['ranking'][data['computer']]:
            utilitySoFar += 10
        # + 10 if extra space
        if self.sp['spaces']['ranking'][space] > self.sp['spaces']['ranking'][data['space']]:
            utilitySoFar += 10
        # * importance
        utilitySoFar *= data['importance']

    def main(self):
        print()
        # print(self.req)
        # print(self.sp)

def dataFusion(req, space):
    #set up limits
    limit = {}
    for i in range (space['globals']['buildingClosedEnd'], 25):
        limit[i] = {
            'computers': copy.deepcopy(space['computers']),
            'spaces': copy.deepcopy(space['spaces']),
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

        #if there is a computer and space that exactly matches their conditions
        for i in range(start, end-hours):
            if limit[i]['spaces'][minSpace] > 0 and limit[i]['computers']['count'][minComp] > 0:
                found = True
                #check to make sure they are available for the entire time they need to work
                for x in range(1,hours):
                    if not limit[i+x]['spaces'][minSpace] > 0 and not limit[i+x]['computers']['count'][minComp] > 0:
                        found = False
                #if they are, then break
                if found:
                    current = i
                    break

        #if there is, give it to them
        if found:
            for x in range(0,hours):
                limit[current+x]['spaces'][minSpace] = limit[current+x]['spaces'][minSpace] - 1
                limit[current+x]['computers']['count'][minComp] = limit[current+x]['computers']['count'][minComp] -1
                limit[current+x]['users'].append(user['name'])
        else:
            notFound.append(user)
        
    #take all users that didnt have conditions that matched exactly, expand their hours
    next = []
    for user in notFound:
        hours = user['hoursNeeded']
        minSpace = user['space']
        minComp = user['computer']
        found = False
        for i in range(space['globals']['buildingClosedEnd'], 25):
            if limit[i]['spaces'][minSpace] > 0 and limit[i]['computers']['count'][minComp] > 0:
                found = True
                #check to make sure they are available for the entire time they need to work
                if hours + i < 25:
                    for x in range(1,hours):
                        if not limit[i+x]['spaces'][minSpace] > 0 and not limit[i+x]['computers']['count'][minComp] > 0:
                            found = False
                #if they are, then break
                if found:
                    current = i
                    break
            #if there is, give it to them
        if found:
            if hours + current < 25:
                for x in range(0,hours):
                    limit[current+x]['spaces'][minSpace] = limit[current+x]['spaces'][minSpace] - 1
                    limit[current+x]['computers']['count'][minComp] = limit[current+x]['computers']['count'][minComp] -1
                    limit[current+x]['users'].append(user['name'])
            else:
                next.append(user)
        else:
            next.append(user)
    
    #TODO: check for a spot that has better equipment than the minimum
    # test = user['space']
    # print(test)
    # print(Size[test].value)

    return limit

def genetic(initial, req):
    # printSchedule(initial, [])
    
    #create generation
    generation = []
    for i in range(0,10):
        generation.append(copy.deepcopy(initial))

    #mutate something in each child
    evolve(generation, req, 10)

def evolve(parentGen, req, gensLeft):
    #for each parent in the generation
    for parent in parentGen:
        #pick something to mutate
        mutate = random.choice(req['users'])

        #take them out of the list
        for x in parent:
            if mutate['name'] in parent[x]['users']:
                parent[x]['users'].remove(mutate['name'])
        
        #add them back to the list in a random place
        addToList(mutate, parent)


def addToList(person, list):
    #TODO: Implement adding person to the list somewhere randomly
    pass

def printSchedule(limit, left):
    for i in range(4,24):
        print(i, limit[i]['users'])
    for x in left:
        print("Could not find a suitable place for", x['name'])



if __name__ == "__main__":
    # requirementsLocation = input(" Requirements location >>> ")
    # spaceLocation = input(" Space location >>> ")
    here = os.path.dirname(os.path.abspath(__file__))
    requirementsLocation = open(os.path.join(here, "test1Requirements.json"),"r")
    spaceLocation = open(os.path.join(here, "test1Space.json"),"r")

    pO = projectOpen(requirementsLocation, spaceLocation)
    pO.main()