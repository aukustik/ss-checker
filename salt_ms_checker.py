#!/usr/bin/python3
from salt import client
from minion import Minion


class MsChecker:

    def run(self):

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
        grains_dict = local_salt.cmd(minions_ids, 'grains.items',tgt_type='list')
        fstab_dict = local_salt.cmd(minions_ids, 'mount.fstab',tgt_type='list')
        
        for minion in available_minions:
            minion.grains = grains_dict[minion.minion_id]
            minion.set_content_mountpoint(fstab_dict[minion.minion_id])


    #     cpu_dict = local_salt.cmd(
    #         minions_ids, 'grains.item', ['cpu_model'], tgt_type='list')


# Формируем список minion_id из созданных объектов
    def get_minions_ids(self, available_minions):
        minions_ids = []
        for minion in available_minions:
            minions_ids.append(minion.minion_id)
        return minions_ids


ms_checker = MsChecker()
ms_checker.run()
