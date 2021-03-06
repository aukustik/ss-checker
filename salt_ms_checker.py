#!/usr/bin/python3
from salt import client
from minion import Minion
import sys

class MsChecker:
    def __init__(self):
        self.ms_type = ''
        self.input_file = ''
        self.local_salt = client.LocalClient()
        self.input_list = []
        self.available_minions = []
        self.available_minions_ids = []
        self.failed_minions_ids = []
        

    def run(self, minions):

        # Проверка активности миньонов
        print('Waiting for a response from minions...')
        self.input_list = self.local_salt.cmd(minions, 'test.ping', tgt_type='list', timeout=5)

        for minion in self.input_list.keys():
            if self.input_list[minion]:
                self.available_minions.append(Minion(minion))

        self.available_minions_ids = self.get_minions_ids(self.available_minions)
        self.failed_minions_ids = self.get_failed_minions(
            self.input_list,
            self.available_minions_ids)
        
        if self.failed_minions_ids:
            self.print_failed_minions(self.failed_minions_ids)

        if self.available_minions:
            self.get_minions_data()
            _report = ''
            for minion in self.available_minions:
                _report += minion.get_info()
                _report += '\n\n'
            # print(_report)
            self.write_to_report_file(_report)
        else:
            print('No available minions')

    def print_failed_minions(self, failed_minions_ids):
        print('\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        print('These minions didn\'t answer:')
        for minion_id in failed_minions_ids:
            print('\t\'{}\''.format(minion_id))
        print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')

# Собираем инфу с миньонов
    def get_minions_data(self):
        print('\nData collection of available minions begins...\n')
        _grains_dict = self.get_grains_dict(self.available_minions_ids)
        _fstab_dict = self.get_fstab_dict(self.available_minions_ids)
        _cpu_info_dict = self.get_cpu_info_dict(self.available_minions_ids)
        _disk_usage = self.get_disk_usage_dict(self.available_minions_ids)
        
        for minion in self.available_minions:
            minion.grains = _grains_dict[minion.minion_id]
            minion.fstab = _fstab_dict[minion.minion_id]
            minion.disk_usage = _disk_usage[minion.minion_id]
            minion.cpu_info = _cpu_info_dict[minion.minion_id]
            minion.set_info_by_ms_type(self.ms_type)

# Получаем список миньонов из файла
    def get_minions_from_file(self, filename):
        _minions_input_file = open(filename,'r')
        _lanes = _minions_input_file.read().splitlines()
        _minions_input_file.close()
        _minions = []
        for lane in _lanes:
            if not lane.startswith('#'):
                _minions.append(lane)
        
        return _minions

    def get_failed_minions(self, full_list, avail_list):
        
        _failed = list(set(full_list) - set(avail_list))

        return _failed

# Формируем список minion_id из созданных объектов
    def get_minions_ids(self, available_minions):
        _minions_ids = []
        for minion in available_minions:
            _minions_ids.append(minion.minion_id)
        return _minions_ids

    def get_grains_dict(self, minions_ids):

        _grains_dict = self.local_salt.cmd(minions_ids, 'grains.items', tgt_type='list')
        print('grains.items received from minions')

        return _grains_dict
    
    def get_fstab_dict(self, minions_ids):

        _fstab_dict = self.local_salt.cmd(minions_ids, 'mount.fstab', tgt_type='list')
        print('mount.fstab received from minions')

        return _fstab_dict
    
    def get_cpu_info_dict(self, minions_ids):

        _cpu_info_dict = self.local_salt.cmd(minions_ids, 'status.cpuinfo', tgt_type='list')
        print('status.cpuinfo received from minions')

        return _cpu_info_dict
    
    def get_disk_usage_dict(self, minions_ids):

        _disk_usage_dict = self.local_salt.cmd(minions_ids, 'disk.usage', tgt_type='list')
        print('disk.usage received from minions')

        return _disk_usage_dict

# Выводим Отчет в файл
    def write_to_report_file(self, report):
        _file_name = 'issues_report.txt'
        _report = open(_file_name, "w")
        _report.write(report)
        print('The report was written to a file {}\n'.format(_file_name))
        _report.close()

if __name__ == '__main__':
    ms_checker = MsChecker()
    #TODO Переписать аргументы через argparse
    if '-h' in sys.argv:
        print('Help:\n Sample:\
            \n  ./salt_ms_checker.py input_file.txt ms_type')
        sys.exit()
    if len(sys.argv) > 2:
        ms_checker.ms_type = sys.argv[-1]
        ms_checker.input_file = sys.argv[-2]
    else:
        print('Not Enough Args')
        sys.exit()

    ms_checker.run(ms_checker.get_minions_from_file(ms_checker.input_file))

