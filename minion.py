from checked_values import *

class Minion:

    def __init__(self, minion_id):
        
        self.info = {}
        self.minion_id = minion_id
        self.grains = None
        self.cpu_info = None
        self.fstab = None
        self.results = {}

    def get_info(self):
        report = '\n"{}":\n'.format(self.minion_id)
        for key in self.info.keys():
            self.results[key] = self.info[key].check()
            if not self.results[key]:
                report += self.info[key].get_report()
        return report
    
    def get_results(self):
        return self.results

    def set_info_by_ms_type(self, ms_type):
        
        if ms_type == 'vod':
            self.info = {
                'content_mountpoint': ContentMountpoint(self.fstab),
                'os': OsRelease(self.grains),
                'gpus': GpusInfo(self.grains)
            }
        elif ms_type == 'ms':
            self.info = {
                'content_mountpoint': ContentMountpoint(self.fstab),
                'os': OsRelease(self.grains),
                'cpu': CpuInfo(self.cpu_info, 4),
                'ram_total': RamTotal(self.grains)
            }
        elif ms_type == 'coder':
            self.info = {
                'content_mountpoint': ContentMountpoint(self.fstab),
                'os': OsRelease(self.grains),
                'cpu': CpuInfo(self.cpu_info, 4),
                'ram_total': RamTotal(self.grains),
                'gpus': GpusInfo(self.grains)
            }

    @property
    def content_mountpoint(self):
        return self.info['content_mountpoint']
    
    @property
    def os(self):
        return self.info['os']
    
    @property
    def ram_total(self):
        return self.info['ram_total']
    
    @property
    def cpu(self):
        return self.info['cpu']

    @property
    def gpus(self):
        return self.info['gpus']