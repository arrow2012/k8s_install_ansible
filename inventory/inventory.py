#!/usr/bin/env python
#!coding:utf-8
from ansible.inventory.manager import InventoryManager
from ansible.inventory.data import InventoryData


class MyInventory(InventoryManager):
    """
    this is my ansible inventory object.
    """
    def __init__(self, loader, sources=None):
        # super(MyInventory, self).__init__(loader,sources=None)

        # base objects
        self._loader = loader
        self._inventory = InventoryData()

        # a list of host(names) to contain current inquiries to
        self._restriction = None
        self._subset = None
        self._sources = sources

        # caches
        self._hosts_patterns_cache = {}  # resolved full patterns
        self._pattern_cache = {}  # resolved individual patterns
        self._inventory_plugins = []  # for generating inventory
        self.gen_inventory()



    def my_add_group(self, groupname, hosts,groupvars=None):

        self._inventory.add_group(groupname)
        my_group = self._inventory.groups[groupname]
        if groupvars:
            for key, value in groupvars.iteritems():
                my_group.set_variable(key, value)
        for host in hosts:
            inventory_hostname = host.get("inventory_hostname")
            hostname = host.get("hostname")
            hostip = host.get("ansible_host")
            hostport = host.get("port")
            self._inventory.add_host(inventory_hostname)

            my_host=self._inventory.get_host(inventory_hostname)
            my_host.set_variable('ansible_host', hostip)
            my_host.set_variable('ansible_port', hostport)

            for key, value in host.iteritems():
                if key not in ["hostname", "port"]:
                    my_host.set_variable(key, value)
            self._inventory.add_group(groupname)
            my_host.add_group(my_group)
            my_group.add_host(my_host)

    def gen_inventory(self):
        if self._sources is None:
            self._sources = []
        elif isinstance(self._sources, list):
            self.my_add_group( 'default_group',self._sources)
        elif isinstance(self._sources, dict):
            self.hostid_list=[]

            for groupname, hosts_and_vars in self._sources.iteritems():
                self.my_add_group(groupname,hosts_and_vars.get("hosts"), hosts_and_vars.get("vars"))
            self._inventory.reconcile_inventory()
        else:
            self._sources = self._sources