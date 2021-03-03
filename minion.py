from checked_values import *

class Minion:

    def __init__(self, minion_id):
        self.info = {
            'content_mountpoint': None,
            'os': None,
            'ram_total': None,
            'cpu': None
        }
        self.minion_id = minion_id

        self.cpu_id = ''
        self.grains = None
        self.cpu_info = None

    def get_info(self):
        
        self.set_os_release(self.grains)
        self.set_ram_total(self.grains)
        self.set_cpu(self.cpu_info)
        self.set_gpus(self.grains)

        for key in self.info.keys():
            self.info[key].check()
        
        result = ''
        result += '"{}":\n'.format(self.minion_id)
        # result += '\tCPU Model: {}\n'.format(self.cpu_id)
        result += '\tOS Release: {} {}\n\t\tSuccess: {} {}\n'.format(
            self.os.distrib,
            self.os.release,
            self.os.result,
            self.os.report)
        result += '\tContent mountpoint is "{}" with filesystem: {}\n\t\tSuccess: {}\n\n'.format(
            self.content_mountpoint.mountpoint,
            self.content_mountpoint.filesystem,
            self.content_mountpoint.result)
        
        result += '\tRAM total: {}\n\t\tSuccess: {} {}\n'.format(
            self.ram_total.size,
            self.ram_total.result,
            self.ram_total.report
        )
        result += '\tCPU model: {} \n\t\tCores: {}\n\t\tThreads: {}\n\t\tSuccess: {} {}\n'.format(
            self.cpu.model,
            self.cpu.cores,
            self.cpu.threads,
            self.cpu.result,
            self.cpu.report
        )
        result += '\tGPUs:{}\n'.format(self.gpus)
        for gpu in self.gpus.gpus_list:
            result += '\t\tVendor: {} Model: {}'.format(
                gpu['vendor'],
                gpu['model']
            )

        return result

    def set_content_mountpoint(self, fstab):
        self.info['content_mountpoint'] = ContentMountpoint(fstab)
    
    def set_os_release(self, grains):
        self.info['os'] = OsRelease(grains)
    
    def set_ram_total(self, grains):
        self.info['ram_total'] = RamTotal(grains)
    
    def set_cpu_info(self, cpu_info):
        self.cpu_info = cpu_info

    def set_cpu(self, grains):
        self.info['cpu'] = CpuInfo(grains)
    
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