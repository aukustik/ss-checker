from checked_values import *

class Minion:

    def __init__(self, minion_id):
        
        self.info = {}
        # self.info = {
        #     'content_mountpoint': None,
        #     'os': None,
        #     'ram_total': None,
        #     'cpu': None
        # }
        self.minion_id = minion_id

        self.cpu_id = ''
        self.grains = None
        self.cpu_info = None
        self.fstab = None


    def get_info(self):
        report = '"{}":\n'.format(self.minion_id)
        for key in self.info.keys():
            self.info[key].check()
            report += self.info[key].get_report()
        return report

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


    def set_content_mountpoint(self, fstab):
        self.info['content_mountpoint'] = ContentMountpoint(fstab)
    
    def set_os_release(self, grains):
        self.info['os'] = OsRelease(grains)
    
    def set_ram_total(self, grains):
        self.info['ram_total'] = RamTotal(grains)

    def set_cpu(self, cpu_info):
        self.info['cpu'] = CpuInfo(cpu_info, 4)
    
    def set_gpus(self, grains):
        self.info['gpus'] = GpusInfo(grains)
    
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