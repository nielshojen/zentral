import copy
import logging
from zentral.contrib.inventory.utils import commit_machine_snapshot_and_trigger_events

__all__ = ['BaseInventory', 'InventoryError']

logger = logging.getLogger('zentral.contrib.inventory.clients.base')


class InventoryError(Exception):
    pass


class BaseInventory(object):
    source_config_secret_attributes = None

    def __init__(self, config_d):
        if not hasattr(self, 'name'):
            self.name = self.__module__.split('.')[-1]
        config_d = copy.deepcopy(config_d)
        config_d.pop('backend')
        if self.source_config_secret_attributes:
            for attr in self.source_config_secret_attributes:
                config_d.pop(attr, None)
        self.source = {'module': self.__module__,
                       'name': self.name,
                       'config': config_d}

    def get_machines(self):
        raise NotImplementedError

    # inventory API
    def sync(self):
        for machine_d in self.get_machines():
            source = copy.deepcopy(self.source)
            try:
                serial_number = machine_d['serial_number']
            except KeyError:
                logger.warning('Machine w/o serial number. Client "%s". Reference "%s"',
                               self.name, machine_d.get('reference', 'Unknown'))
                continue
            if not serial_number:
                logger.warning('Machine serial number blank. Client "%s". Reference "%s"',
                               self.name, machine_d.get('reference', 'Unknown'))
                continue
            # source will be modified by mto
            machine_d['source'] = source
            for group_d in machine_d.get('groups', []):
                group_d['source'] = source
            business_unit_d = machine_d.get('business_unit', None)
            if business_unit_d:
                business_unit_d['source'] = source
            # save all
            commit_machine_snapshot_and_trigger_events(machine_d)

    def add_machine_to_group(self, machine_snapshot, group_name):
        raise NotImplementedError
