import json
import os

class Settings:
    def __init__(self):
        self.dateFormat = ""
        self.badImagePrefix = ""
        self.defaultImageFolder = ""
        self.updateDefaultImageFolderOnLoad = False

    def loadJson(self):
        if not os.path.exists("settings.json"):
            print("Settings file not found, creating one with default values...")

            # Populate settings with default values
            self.dateFormat = "%Y-%m-%d"
            self.badImagePrefix = "BAD_"
            self.defaultImageFolder = os.path.join(os.path.expanduser("~"), "Pictures")
            self.updateDefaultImageFolderOnLoad = False

            print(self.toJson())

            # Create the settings file if it doesn't exist
            self.saveJson()

        # Load the settings from the json file
        f = open("settings.json", "r")
        self.fromJson(f.read())

    def saveJson(self):
        # Save the dictionary to a json file
        f = open("settings.json", "w")
        f.write(self.toJson())
        f.close()

        print("Settings saved to json file:")
        print(self.toJson())

    def toJson(self):
        return json.dumps(self.__dict__)
    
    def fromJson(self, jsonStr):
        self.__dict__ = json.loads(jsonStr)

        print("Settings loaded from json file:")
        print(self.toJson())