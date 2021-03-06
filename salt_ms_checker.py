#!/usr/bin/python3
from salt import client
from minion import Minion
import sys
import argparse

class MsChecker:
    def __init__(self):
        self.ms_type = ''
        self.input_file = ''
        self.verbose = False
        self.local_salt = client.LocalClient()
        self.input_list = []
        self.available_minions = []
        self.available_minions_ids = []
        self.failed_minions_ids = []
        with open('qs_base.txt') as _qs_base:
            self.qs_base_list = _qs_base.read().splitlines()

    def run(self):
        _minions = self.get_minions_from_file(self.input_file)
        # Проверка активности миньонов
        print('Waiting for a response from minions...')
        self.input_list = self.local_salt.cmd(_minions, 'test.ping', tgt_type='list', timeout=5)

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
            minion.qs_base_list = self.qs_base_list
            minion.verbose = self.verbose
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

def prepare_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='Name of input file with minion ids')
    parser.add_argument('ms_type', help='Type of Media Server (ms, coder, vod)')
    parser.add_argument('--verbose', help='Full report with success tests',
        action="store_true")
    
    return parser

if __name__ == '__main__':
    ms_checker = MsChecker()
    parser = prepare_argparser()
    args = parser.parse_args()    
    ms_checker.ms_type = args.ms_type
    ms_checker.input_file = args.input_file
    ms_checker.verbose = args.verbose

    ms_checker.run()