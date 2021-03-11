import re

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
        if type(self.fstab) is dict:
            if '/home/telebreeze/media' in self.fstab.keys():
                return '/home/telebreeze/media'

            elif '/home/telebreeze/' in self.fstab.keys():
                return '/home/telebreeze'

            elif '/home' in self.fstab.keys():
                return '/home'

            else:
                return '/'
        
        else:
            return None

# Проверяем FS у маунтпоинта с контентом.
    def get_mountpoint_filesystem(self):
        if self.mountpoint != None:
            _filesystem = self.fstab[self.mountpoint]['fstype']
            return _filesystem
        else:
            return None

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
        _report = '\n\t- RAM total: {} GB'.format(self.ram_mb_to_gb(self.size))
        _report += self.report
        return _report
    
    def ram_mb_to_gb(self, size_mb):
        _size_gb = float(size_mb) / 1000
        _size_gb = float('{0:.3f}'.format(_size_gb))
        return _size_gb

    
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
        _report = '\n\t- CPU:\n\t\t- Model: {}'.format(self.model)
        _report += '\n\t\t- Cores: {}\n\t\t- Threads: {}\n'.format(
            self.cores,
            self.threads
        )
        if self.report != '':
            _report += '\n\t\t- Report: {}'.format(self.report)
        return _report

class QSInfo(CheckedValue):
    def __init__(self, cpu_info, qs_base):
        self.cpu_model = cpu_info['model name']
        _proc_index = re.search(
            '(i\d+|W|E\d|L)-?[0-9]+\w{1,3}(\sv[0-9]|\s)', self.cpu_model)
        self.proc_index = _proc_index.group(0).strip()
        self.qs_base_list = qs_base
        super(QSInfo, self).__init__()

# Проверка процессора на наличие в базе процов с QSync
    def check(self):
        if self.proc_index in self.qs_base_list:
            self.result = True
            return self.result
        else:
            self.result = False
            return self.result
    
    def get_report(self):
        _report = '\n\n\t- QuickSync:\n'
        if self.result:           
            _report += '\t\t- Intel Quick Sync is available for {}'.format(
                self.cpu_model
            )
        else:
            _report += '\t\t- Intel Quick Sync is unavailable for {}'.format(
                self.cpu_model
            )
        return _report

class DiskUsage(CheckedValue):

    def __init__(self, disk_usage, fstab):
        self.disk_usage = disk_usage
        self.fstab = fstab
    
    def check(self):
        self.result = True
        return self.result
    
    def get_report(self):
        _report = '\n\t- Partitions:'

        for partition in self.disk_usage.keys():
            if partition in self.fstab.keys():
                _report += '\n\t\t"{}":\n'.format(partition)
                _report += '\t\t\tfilesystem: {}\n'.format(self.fstab[partition]['fstype'])
                _report += '\t\t\ttotal: {} GB\n'.format(
                    self.kb_units_to_gb(self.disk_usage[partition]['1K-blocks'])
                )
                _report += '\t\t\tavailable: {} GB\n'.format(
                    self.kb_units_to_gb(self.disk_usage[partition]['available'])
                )
        
        return _report

    def kb_units_to_gb(self, kb_units):
        _gb_units = float(kb_units) / 1048576
        _gb_units = float('{0:.3f}'.format(_gb_units))
        return _gb_units
