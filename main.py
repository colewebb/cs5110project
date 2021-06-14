import json

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
        else:
            print("Error 1")
            exit(1)

    def main(self):
        print(self.req)
        print(self.sp)



if __name__ == "__main__":
    requirementsLocation = input(" Requirements location >>> ")
    spaceLocation = input(" Space location >>> ")
    pO = projectOpen(requirementsLocation, spaceLocation)
    pO.main()