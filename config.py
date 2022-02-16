from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class SodaConfig(object):
    def __init__(self, *args, **kwargs):

        self.file_name = 'config.yaml'

        with open(self.file_name, 'r') as filehandle:
            self.raw_config = load(filehandle, Loader=Loader)

        self.flavors = self.raw_config['flavors']
        self.cal_values = self.raw_config['calibration']

    def save_config(self):
        with open(self.file_name, 'w') as fileout:
            self.raw_config['flavors'] = self.flavors
            self.raw_config['calibration'] = self.calibration

            dump(self.raw_config, fileout, Dumper=Dumper)
