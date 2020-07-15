#!/usr/bin/env python
#!coding:utf-8

import json
import shutil
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager

from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from ansible import context
import ansible.constants as C

from task import task
from inventory import inventory

class ResultCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin
    """
    def v2_runner_on_ok(self, result, **kwargs):
        """Print a json representation of the result

        This method could store the result in an instance attribute for retrieval later
        """
        host = result._host
        print (u"======================= %s 执行结果======================= " % result._task)
        print(json.dumps({"test":"result._result.task", host.name: result._result}, indent=4))

# since the API is constructed for CLI it expects certain options to always be set in the context object
context.CLIARGS = ImmutableDict(connection='local', module_path=['/to/mymodules'], forks=10, become=None,
                                become_method=None, become_user=None, check=False, diff=False)

# initialize needed objects
loader = DataLoader() # Takes care of finding and reading yaml, json and ini files
passwords = dict(vault_pass='secret')

# Instantiate our ResultCallback for handling results as they come in. Ansible expects this to be one of its main display outlets
results_callback = ResultCallback()


with open('inventory/hosts.json','r',encoding='utf8') as f:
    json_data = json.load(f)
    print('这是文件中的json数据：',json_data)

inventory = inventory.MyInventory(loader=loader,sources=json_data)
# create inventory, use path to host config file as source or inventory in a comma separated string
inventory = InventoryManager(loader=loader, sources='localhost,')

# variable manager takes care of merging all the different sources to give you a unified view of variables available in each context
variable_manager = VariableManager(loader=loader, inventory=inventory)


t = task.Task()

# create data structure that represents our play, including tasks, this is basically what our YAML loader does internally.
play_source = [
    dict(
        name="Ansible Play",
        hosts='master',
        gather_facts='no',
        tasks=[
            t.install_ntp(),
        ]
    ),
    dict(
        name="Ansible Play",
        hosts='master',
        gather_facts='no',
        tasks=[
            t.set_timezone(),
        ]
    )
]

# Create play object, playbook objects use .load instead of init or new methods,
# this will also automatically create the task objects from the info provided in play_source
play = Play().load(
    play_source,
    variable_manager=variable_manager, loader=loader
)

# Run it - instantiate task queue manager, which takes care of forking and setting up all objects to iterate over host list and tasks
tqm = None
try:
    tqm = TaskQueueManager(
        inventory=inventory,
        variable_manager=variable_manager,
        loader=loader,
        passwords=passwords,
        stdout_callback=results_callback,  # Use our custom callback instead of the ``default`` callback plugin, which prints to stdout
    )
    result = tqm.run(play) # most interesting data for a play is actually sent to the callback's methods

finally:
    # we always need to cleanup child procs and the structures we use to communicate with them
    if tqm is not None:
        tqm.cleanup()

    # Remove ansible tmpdir
    shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)