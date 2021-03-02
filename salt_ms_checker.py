#!/usr/bin/python3
from salt import client


class MsChecker:

    def run(self):

        local_salt = client.LocalClient()

        temp = local_salt.cmd('*', 'test.ping', timeout=5)
        available_minions = []

        for minion in temp.keys():
            if temp[minion]:
                available_minions.append(Minion(minion))

        if available_minions:
            self.get_info(available_minions, local_salt)

            for minion in available_minions:
                print(minion.get_info())
        
        else:
            print('No available minions')

    def get_info(self, available_minions, local_salt):

        minions_ids = self.get_minions_ids(available_minions)

        cpu_dict = local_salt.cmd(
            minions_ids, 'grains.item', ['cpu_model'], tgt_type='list')

        mp_home_dict = local_salt.cmd(
            minions_ids, 'mount.fstab', tgt_type='list')

        os_dict = local_salt.cmd(
            minions_ids, 'grains.item', ['os'], tgt_type='list')

        os_release_dict = local_salt.cmd(
            minions_ids, 'grains.item', ['osrelease'], tgt_type='list')

        grains_full_dict = local_salt.cmd(
            minions_ids, 'grains.items', tgt_type='list')

        for minion in available_minions:

            minion.cpu_id = cpu_dict[minion.minion_id]['cpu_model']

            if ('/home' in mp_home_dict[minion.minion_id]):
                minion.homefs = mp_home_dict[minion.minion_id]['/home']['fstype']
            else:
                minion.homefs = 'Unmounted'

            minion.os = os_dict[minion.minion_id]['os']
            minion.os_release = os_release_dict[minion.minion_id]['osrelease']

            for gpu in grains_full_dict[minion.minion_id]['gpus']:
                minion.gpus += '\n\t\tVendor: {}\n'.format(gpu['vendor'])
                minion.gpus += '\t\tModel: {}\n'.format(gpu['model'])

    def get_minions_ids(self, available_minions):
        minions_ids = []
        for minion in available_minions:
            minions_ids.append(minion.minion_id)
        return minions_ids


class Minion:

    def __init__(self, minion_id):
        self.minion_id = minion_id
        self.homefs = None
        self.cpu_id = None
        self.os = None
        self.os_release = '9.9.9'
        self.gpus = ''

    def get_info(self):
        result = ''
        result += 'minion_id: "{}"\n'.format(self.minion_id)
        result += '\t/home mountpoint filesystem: {}\n'.format(
            self.check_home_mp())
        result += '\tCPU Model: {}\n'.format(self.cpu_id)
        result += '\tOS Release: {} {}\n'.format(
            self.os,
            self.os_release)
        result += '\tGPUs:{}\n'.format(self.gpus)
        result += self.check_release()

        return result

    def check_home_mp(self):
        if (self.homefs == 'ext4'):
            self.homefs += ' (SUCCESS)'
        else:
            self.homefs += ' (FAIL) must be "ext4"'

        return self.homefs

    def check_release(self):
        info = ''
        release_list = self.os_release.split('.')
        if int(release_list[0]) < 7 or int(release_list[0]) > 7:
            info += '\tWrong OS Version\nPlease, install CentOS 7.'
            return info
        
        if int(release_list[1]) <= 4:
            info += '\tOS supports Intel QuickSync.\n'
        else:
            info += '\n\tOS not supports Intel QuickSync.\n'
            info += '\tYou need CentOS 7.4 or lower.\n'
        return info

ms_checker = MsChecker()
ms_checker.run()
