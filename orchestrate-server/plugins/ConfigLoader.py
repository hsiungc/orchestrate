"""# Class Object to call in data from config file
# TODO: apply method for different file type"""
import yaml


class ConfigLoader():
    def __init__(self):
        self.file_obj = None


    def loadYaml(self, filename):
        """
            Read Parameter file in the form of yml
            The FullLoader parameter handles the conversion from YAML
            Scalar values to Python the dictionary format
        """
        with open(f'{filename}', encoding='utf8') as file:
            file_obj = yaml.load(file, Loader=yaml.FullLoader)
        self.file_obj = file_obj
        return self.file_obj


    



