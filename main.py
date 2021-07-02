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


    def utility(self, user, computer, space):
        # start with some utility, since this is work going on available hours and that is good
        utilitySoFar = 20
        data = None
        for u in self.req['users']:
            if u['name'] == user:
                data = u
        if data == None:
            raise ArithmeticError
        # +- 10 if computational needs met
        if self.sp['computers']['ranking'][computer] >= self.sp['computers']['ranking'][data['computer']]:
            utilitySoFar += 10
        else:
            utilitySoFar -= 10
        # +- 5 if space needs met
        if self.sp['spaces']['ranking'][space] >= self.sp['spaces']['ranking'][data['space']]:
            utilitySoFar += 5
        else:
            utilitySoFar -= 5
        # + 1 if extra computational power
        if self.sp['computers']['ranking'][computer] > self.sp['computers']['ranking'][data['computer']]:
            utilitySoFar += 1
        # + 1 if extra space
        if self.sp['spaces']['ranking'][space] > self.sp['spaces']['ranking'][data['space']]:
            utilitySoFar += 1
        # * importance
        utilitySoFar *= data['importance']
        return utilitySoFar


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
        if found:
            for x in range(0,hours):
                limit[current+x]['spaces']['count'][minSpace] = limit[current+x]['spaces']['count'][minSpace] - 1
                limit[current+x]['computers']['count'][minComp] = limit[current+x]['computers']['count'][minComp] -1
                limit[current+x]['users'].append({'name': user['name'],'comp':minComp, 'space': minSpace})
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
            if limit[i]['spaces']['count'][minSpace] > 0 and limit[i]['computers']['count'][minComp] > 0:
                found = True
                #check to make sure they are available for the entire time they need to work
                if hours + i < 25:
                    for x in range(1,hours):
                        if not limit[i+x]['spaces']['count'][minSpace] > 0 and not limit[i+x]['computers']['count'][minComp] > 0:
                            found = False
                #if they are, then break
                if found:
                    current = i
                    break
            #if there is, give it to them
        if found:
            if hours + current < 25:
                for x in range(0,hours):
                    limit[current+x]['spaces']['count'][minSpace] = limit[current+x]['spaces']['count'][minSpace] - 1
                    limit[current+x]['computers']['count'][minComp] = limit[current+x]['computers']['count'][minComp] -1
                    limit[current+x]['users'].append({'name': user['name'],'comp':minComp, 'space': minSpace})
            else:
                next.append(user)
        else:
            next.append(user)
    
    #TODO: check for a spot that has better equipment than the minimum

    return limit

def genetic(initial, req):    
    #create generation
    generation = []
    for i in range(0,4):
        generation.append(copy.deepcopy(initial))

    #mutate something in each child
    best = evolve(generation, req, 10)
    printSchedule(best, [])

def evolve(parentGen, req, gensLeft):
    if gensLeft <= 0:
        return parentGen[0]

    #double generation by copying each parent
    temp = copy.deepcopy(parentGen)
    parentGen = parentGen + temp

    #for each parent in the generation
    for parent in parentGen:
        #pick something to mutate
        mutate = random.choice(req['users'])

        #take them out of the list
        for x in parent:
            for i in parent[x]['users']:
                if mutate['name'] in i['name']:
                    #remove their name from the list and add back their resources
                    current = parent[x]
                    current['spaces']['count'][i['space']] = current['spaces']['count'][i['space']] + 1
                    current['computers']['count'][i['comp']] = current['computers']['count'][i['comp']] + 1
                    current['users'].remove(i)

        #add them back to the list in a random place
        addToList(mutate, parent)

    # TODO: Find utility of every parent

    # TODO: Sort generation by utility

    #remove the lowest half of generation
    child = parentGen[len(parentGen)//2:]

    #move on to next generation
    best = evolve(child, req, gensLeft-1)
    return best


def addToList(person, list):
    #choose random location
    start = random.randrange(4,24)
    count = 0
    choices = []
    for i in range (start,24):
        computers = list[i]['computers']['count']
        spaces = list[i]['spaces']['count']
        avail = getAvailable(list, i)
        if len(avail['computers']) > 0 and len(avail['spaces']) > 0:
            compChoice = random.choice(avail['computers'])
            spaceChoice = random.choice(avail['spaces'])
            choices.append({'comp':compChoice, 'space':spaceChoice})
            count = count + 1
            # print(compChoice, spaceChoice)
            if count == person['hoursNeeded']+1:
                counter = 0
                for x in range(i-person['hoursNeeded'],i):
                    current = list[x]
                    current['spaces']['count'][choices[counter]['space']] = current['spaces']['count'][choices[counter]['space']] - 1
                    current['computers']['count'][choices[counter]['comp']] = current['computers']['count'][choices[counter]['comp']] -1
                    current['users'].append({'name': person['name'],'comp':choices[counter]['comp'], 'space': choices[counter]['space']})
                    counter = counter + 1
        else:
            choices = []
            count = 0
            continue
        
    # for i in range (4,start):

def printSchedule(limit, left):
    for i in range(4,24):
        print(i, limit[i]['users'])
    for x in left:
        print("Could not find a suitable place for", x['name'])

def printResources(list, index):
    print(list[index]['computers']['count'])
    print(list[index]['spaces']['count'])

def getAvailable(list, index):
    computers = []
    spaces = []
    for x in list[index]['computers']['count']:
        if list[index]['computers']['count'].get(x) > 0:
            computers.append(x)

    for x in list[index]['spaces']['count']:
        if list[index]['spaces']['count'].get(x) > 0:
            spaces.append(x)

    return {'computers': computers, 'spaces':spaces}

if __name__ == "__main__":
    # requirementsLocation = input(" Requirements location >>> ")
    # spaceLocation = input(" Space location >>> ")
    here = os.path.dirname(os.path.abspath(__file__))
    requirementsLocation = open(os.path.join(here, "test1Requirements.json"),"r")
    spaceLocation = open(os.path.join(here, "test1Space.json"),"r")

    pO = projectOpen(requirementsLocation, spaceLocation)