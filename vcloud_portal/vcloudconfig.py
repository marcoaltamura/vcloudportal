from json import load
import os.path, time

class VCloudDirectorConfiguration:
    def __init__(self):
        self.baseurl = None
        self.apitoken = None
        self.path = None
        self.config_last_modified = os.path.getmtime('config/config.json')

        self.read_config()
        self.is_config_changed()

    def read_config(self):
        if self.path is None or self.is_config_changed():
            self.reload_config()
        return self.path

    def get_baseurl(self):
        return self.baseurl
    
    def get_apitoken(self):
        return self.apitoken
    
    def reload_config(self):
        try:
            # read JSON config file
            with open('config/config.json') as config_file:
                parameters = load(config_file)
                config_file.close()
        except FileNotFoundError as exc_msg:
            print(f"Unable to find config file! {exc_msg}")
        try:
            self.baseurl = parameters['baseurl']
            self.apitoken = parameters['apitoken']
        except KeyError as exc_msg:
            print(f"Unable to connect! {exc_msg} parameter missing in config file!")

    def is_config_changed(self):
        current_time = time.time()
        return self.config_last_modified <= current_time - 10