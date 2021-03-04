#!/usr/bin/python3
from salt import client
from minion import Minion
import sys

class MsChecker:

    def run(self, minions):
        if len(sys.argv) > 1:
            self.ms_type = sys.argv[-1]
        else:
            print('No Args')
            sys.exit()

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
        minions = minions_input_file.read().splitlines()
        minions_input_file.close()
        return minions

if __name__ == '__main__':
    ms_checker = MsChecker()
    print(ms_checker.get_minions_from_file('input.txt'))
    ms_checker.run(ms_checker.get_minions_from_file('input.txt'))

