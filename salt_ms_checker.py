#!/usr/bin/python3
from salt import client
from minion import Minion
import sys

class MsChecker:
    def __init__(self):
        self.ms_type = ''
        self.input_file = ''

    def run(self, minions):

        local_salt = client.LocalClient()

        temp = local_salt.cmd(minions, 'test.ping', tgt_type='list', timeout=5)
        available_minions = []

        for minion in temp.keys():
            if temp[minion]:
                available_minions.append(Minion(minion))

        if available_minions:
            self.get_data(available_minions, local_salt)

            for minion in available_minions:
                print(minion.get_info())
                print(minion.get_results())
        
        else:
            print('No available minions')

    def get_data(self, available_minions, local_salt):

        minions_ids = self.get_minions_ids(available_minions) 
        grains_dict = local_salt.cmd(minions_ids, 'grains.items', tgt_type='list')
        fstab_dict = local_salt.cmd(minions_ids, 'mount.fstab', tgt_type='list')
        cpu_info_dict = local_salt.cmd(minions_ids, 'status.cpuinfo', tgt_type='list')
        
        for minion in available_minions:
            minion.grains = grains_dict[minion.minion_id]
            minion.fstab = fstab_dict[minion.minion_id]
            minion.cpu_info = cpu_info_dict[minion.minion_id]
            minion.set_info_by_ms_type(self.ms_type)

# Формируем список minion_id из созданных объектов
    def get_minions_ids(self, available_minions):
        minions_ids = []
        for minion in available_minions:
            minions_ids.append(minion.minion_id)
        return minions_ids

    def get_minions_from_file(self, filename):
        minions_input_file = open(filename,'r')
        lanes = minions_input_file.read().splitlines()
        minions_input_file.close()
        minions = []
        for lane in lanes:
            if not lane.startswith('#'):
                minions.append(lane)
        
        return minions

if __name__ == '__main__':
    ms_checker = MsChecker()
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

