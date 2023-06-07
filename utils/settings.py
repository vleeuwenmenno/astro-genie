import json
import os

class Settings:
    def __init__(self):
        self.dateFormat = ""
        self.badImagePrefix = ""

        self.loadJson()

    def loadJson(self):
        if not os.path.exists("settings.json"):
            # Populate settings with default values
            self.dateFormat = "%Y-%m-%d"
            self.badImagePrefix = "BAD_"

            # Create the settings file if it doesn't exist
            self.saveJson()

        # Load the settings from the json file
        f = open("settings.json", "r")
        settingsDict = json.loads(f.read())

        # Set the settings variables
        self.dateFormat = settingsDict["dateFormat"]
        self.badImagePrefix = settingsDict["badImagePrefix"]

    def saveJson(self):
        # Combine all settings into a dictionary
        settingsDict = {
            "dateFormat": self.dateFormat,
            "badImagePrefix": self.badImagePrefix
        }

        # Save the dictionary to a json file
        f = open("settings.json", "w")
        f.write(json.dumps(settingsDict))
        f.close()