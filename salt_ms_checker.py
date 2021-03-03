#!/usr/bin/python3
from salt import client
from minion import Minion
import sys

class MsChecker:

    def run(self):
        if len(sys.argv) > 1:
            self.ms_type = sys.argv[-1]
        else:
            print('No Args')
            sys.exit()

        local_salt = client.LocalClient()

        temp = local_salt.cmd('*', 'test.ping', timeout=5)
        available_minions = []

        for minion in temp.keys():
            if temp[minion]:
                available_minions.append(Minion(minion))

        if available_minions:
            self.get_grains(available_minions, local_salt)

            for minion in available_minions:
                print(minion.get_info())
        
        else:
            print('No available minions')

    def get_grains(self, available_minions, local_salt):

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


if __name__ == '__main__':
    ms_checker = MsChecker()
    ms_checker.run()

