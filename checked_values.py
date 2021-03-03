class CheckedValue:
    def __init__(self):
        self.result = False
        self.report = ''
    
    def check(self):
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
            mountpoint = '/home/telebreeze/media'
            return mountpoint
        
        elif '/home/telebreeze/' in self.fstab.keys():
            mountpoint = '/home/telebreeze'
            return mountpoint

        elif '/home' in self.fstab.keys():
            mountpoint = '/home'
            return mountpoint
        
        else:
            mountpoint = '/'
            return mountpoint

# Проверяем FS у маунтпоинта с контентом.
    def get_mountpoint_filesystem(self):
        
        filesystem = self.fstab[self.mountpoint]['fstype']
        return filesystem

    def check(self):

        if (self.filesystem == 'ext4'):
            self.result = True
            return self.result
        else:
            self.result = False
            return self.result

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
            self.report += '\n\t\tUnsupported Linux distrib.\n'
            return self.result
        
        release_list = self.release.split('.')
        if release_list[0] != '7':
            self.result = False
            self.report += '\n\t\tUnsupported CentOS Verison\n'
            return self.result
        
        elif int(release_list[1]) > 4:
            self.result = True
            self.report += '\n\t\tIntelGPU unsupported for this os release.\n'
            return self.result
        
        else:
            self.result = True
            return self.result


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
    
class CpuInfo(CheckedValue):
    def __init__(self, cpu_info):
        self.model = cpu_info['model name']
        self.cores = cpu_info['cpu cores']
        self.threads = cpu_info['siblings']
        super(CpuInfo, self).__init__()
    
    def check(self):
        if int(self.cores) < 4:
            self.result = False
            self.report += '\n\t\tThere is not enough CPU cores on the server.\n'
            return self.result
        
        else:
            self.result = True
            return self.result

class GpusInfo(CheckedValue):
    def __init__(self, grains):
        self.gpus_list = grains['gpus']
        
    def check(self):
        self.result = True
        return self.result