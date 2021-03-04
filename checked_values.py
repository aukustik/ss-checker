class CheckedValue:
    def __init__(self):
        self.result = False
        self.report = ''
    
    def check(self):
        raise NotImplementedError

    def get_report(self):
        raise NotImplementedError


class ContentMountpoint(CheckedValue):
    
    def __init__(self, fstab):
        super(ContentMountpoint, self).__init__()
        self.fstab = fstab
        self.mountpoint = self.get_content_mountpoint()
        self.filesystem = self.get_mountpoint_filesystem()

# Ищем маунтпоинт с контентом. Начинаем с /home/telebreeze/media, если его нет, идем выше.
    def get_content_mountpoint(self): 
        
        if '/home/telebreeze/media' in self.fstab.keys():
            return '/home/telebreeze/media'
             
        elif '/home/telebreeze/' in self.fstab.keys():
            return '/home/telebreeze'

        elif '/home' in self.fstab.keys():
            return '/home'
        
        else:
            return '/'

# Проверяем FS у маунтпоинта с контентом.
    def get_mountpoint_filesystem(self):
        
        _filesystem = self.fstab[self.mountpoint]['fstype']
        return _filesystem

    def check(self):

        if (self.filesystem == 'ext4'):
            self.result = True
            return self.result
        else:
            self.result = False
            return self.result
    
    def get_report(self):
        _report = ''
        _report += '\n\t- Content mountpoint is "{}" with filesystem {}\n'.format(
            self.mountpoint,
            self.filesystem
        )
        return _report


class OsRelease(CheckedValue):
    
    def __init__(self, grains):
        self.distrib = grains['os']
        self.release = grains['osrelease']
        super(OsRelease, self).__init__()

# Проверяем название Дистрибутива. Если не ок - заканчиваем проверку
# и репортим об ошибке. Повторям для всех условий.   
    def check(self):

        if self.distrib != 'CentOS':
            self.result = False
            self.report += '\n\t\t\tUnsupported Linux distrib.\n'
            return self.result
        
        _release_list = self.release.split('.')
        if _release_list[0] != '7':
            self.result = False
            self.report += '\n\t\t\tUnsupported CentOS Verison\n'
            return self.result
        
        elif int(_release_list[1]) > 4:
            self.result = True
            self.report += '\n\t\t\tIntelGPU unsupported for this os release.\n'
            return self.result
        
        else:
            self.result = True
            return self.result

    def get_report(self):
        _report = '\n\n\t- OS:\n'
        _report += '\t\t- {} {}'.format(
            self.distrib,
            self.release
        )
        _report += '\n\t\t- Report: {}'.format(self.report)
        return _report

class RamTotal(CheckedValue):
    def __init__(self, grains):
        self.size = grains['mem_total']
        super(RamTotal, self).__init__()

# Проверяем общее количество RAM.
# Проверку выставил временную.
    def check(self):
        if int(self.size) < 15000:
            self.result = False
            self.report += '\n\t\tThere is not enough RAM on the server.\n'
            return self.result
        
        else:
            self.result = True
            return self.result
    
    def get_report(self):
        _report = '\n\t- RAM total: {}Mb'.format(self.size)
        _report += self.report
        return _report
    
class CpuInfo(CheckedValue):
    def __init__(self, cpu_info, min_threads):
        self.model = cpu_info['model name']
        self.cores = cpu_info['cpu cores']
        self.threads = cpu_info['siblings']
        self.min_threads = min_threads
        super(CpuInfo, self).__init__()
    
    def check(self):
        if int(self.cores) < self.min_threads:
            self.result = False
            self.report += 'There is not enough CPU cores on the server.\n'
            return self.result
        
        else:
            self.result = True
            return self.result
    
    def get_report(self):
        _report = '\t- CPU:\n\t\t- Model: {}'.format(self.model)
        _report += '\n\t\t- Cores: {}\n\t\t- Threads: {}'.format(
            self.cores,
            self.threads
        )
        _report += '\n\t\t- Report: {}'.format(self.report)
        return _report

class GpusInfo(CheckedValue):
    def __init__(self, grains):
        self.gpus_list = grains['gpus']
        
    def check(self):
        self.result = True
        return self.result
    
    def get_report(self):
        _report = '\t- GPUs:'
        for gpu in self.gpus_list:
            _report += '\n\t\t- Vendor: {} Model: {}'.format(
                gpu['vendor'],
                gpu['model']
            )
        return _report
