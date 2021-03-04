#!/usr/bin/python3
from salt import client
from minion import Minion
import sys

class MsChecker:
    def __init__(self):
        self.ms_type = ''
        self.input_file = ''

    def run(self, minions):

        _local_salt = client.LocalClient()

        # Проверка активности миньонов
        _temp = _local_salt.cmd(minions, 'test.ping', tgt_type='list', timeout=5)
        _available_minions = []

        for minion in _temp.keys():
            if _temp[minion]:
                _available_minions.append(Minion(minion))

        if _available_minions:
            self.get_minions_data(_available_minions, _local_salt)
            _report = ''
            for minion in _available_minions:
                _report += minion.get_info()
                _report += str(minion.get_results())
                _report += '\n\n'
            print(_report)
            self.write_to_report_file(_report)
        else:
            print('No available minions')

# Собираем инфу с миньонов
    def get_minions_data(self, available_minions, local_salt):

        _minions_ids = self.get_minions_ids(available_minions) 
        _grains_dict = local_salt.cmd(_minions_ids, 'grains.items', tgt_type='list')
        _fstab_dict = local_salt.cmd(_minions_ids, 'mount.fstab', tgt_type='list')
        _cpu_info_dict = local_salt.cmd(_minions_ids, 'status.cpuinfo', tgt_type='list')
        
        for minion in available_minions:
            minion.grains = _grains_dict[minion.minion_id]
            minion.fstab = _fstab_dict[minion.minion_id]
            minion.cpu_info = _cpu_info_dict[minion.minion_id]
            minion.set_info_by_ms_type(self.ms_type)

# Формируем список minion_id из созданных объектов
    def get_minions_ids(self, available_minions):
        _minions_ids = []
        for minion in available_minions:
            _minions_ids.append(minion.minion_id)
        return _minions_ids

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

# Выводим Отчет в файл
    def write_to_report_file(self, report):
        _report = open("issues_report.txt", "w")
        _report.write(report)
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

    print(ms_checker.get_minions_from_file(ms_checker.input_file))
    ms_checker.run(ms_checker.get_minions_from_file(ms_checker.input_file))

