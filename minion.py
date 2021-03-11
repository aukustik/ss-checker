from checked_values import *
import sys

class Minion:

    def __init__(self, minion_id):
        
        self.info = {} # Параметры для проверки
        self.minion_id = minion_id # ID Миньона
        self.grains = None # Все Grains
        self.cpu_info = None # Информация о ЦПУ
        self.fstab = None # Содержимое fstab
        self.results = {} # Результаты проверок
        self.disk_usage = {} # Инфо о дисках
        self.qs_base_list = [] # База процессоров с QSync
        self.verbose = False # Формат репорта

    def get_info(self):
        _report = '"{}":\n'.format(self.minion_id)
        for key in self.info.keys():
            self.results[key] = self.info[key].check()
            if self.verbose:
                _report += self.info[key].get_report()
            else:
                if not self.results[key]:                
                    _report += self.info[key].get_report()

        return _report
    
    def get_results(self):
        return self.results

    def set_info_by_ms_type(self, ms_type):
        
        if ms_type == 'vod':
            self.info = {
                'content_mountpoint': ContentMountpoint(self.fstab),
                'os': OsRelease(self.grains),
                'gpus': QSInfo(self.cpu_info, self.qs_base_list)
            }
        elif ms_type == 'ms':
            self.info = {
                'content_mountpoint': ContentMountpoint(self.fstab),
                'os': OsRelease(self.grains),
                'cpu': CpuInfo(self.cpu_info, 1),
                'ram_total': RamTotal(self.grains, 7800)
            }
        elif ms_type == 'coder':
            self.info = {
                'disks': DiskUsage(self.disk_usage, self.fstab),
                'content_mountpoint': ContentMountpoint(self.fstab),
                'os': OsRelease(self.grains),
                'cpu': CpuInfo(self.cpu_info, 4),
                'ram_total': RamTotal(self.grains, 7800),
                'gpus': QSInfo(self.cpu_info, self.qs_base_list)
            }
        else:
            print('MS type is incorrect, exit...')
            sys.exit()