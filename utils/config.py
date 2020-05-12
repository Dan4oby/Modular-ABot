# файл, позволяющий работать с config.json
import json


class Config:
    def __init__(self):
        self.file = "config.json"
        configFile = open(self.file, "r")
        self.config = json.load(configFile)
        configFile.close()

    def getConfigVar(self, variable):
        if variable in self.config.keys():
            return self.config[variable]

    def setConfigVar(self, variable, arg):
        if variable in self.config.keys():
            self.config[variable] = arg
        with open(self.file, 'w') as config:
            config.write(json.dumps(self.config, separators=(',\n', ': ')))
