#/bin/bash/env python
 
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
 
# set options for play
Options = namedtuple('Options', ['connection', 'module_path', 'forks',
                                 'become', 'become_method', 'become_user', 'check'])
 
#initialize needed objects
variable_manager = VariableManager()
loader = DataLoader()
options = Options(connection='', module_path='', forks=100, become=True,
                  become_method='sudo', become_user='root', check=False)
passwords = dict(vault_pass='secret')
 
#create inventory and pass to var manager
inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list='/etc/ansible/hosts')
variable_manager.set_inventory(inventory)
 
#create play with tasks
play_src = dict(
            name="bandwidth",
            hosts="cloud",
            gather_facts="no",
            become="true",
            tasks=[
                 #dict(name="Check whether the package is installed or not", action=dict(module="apt", args=dict(name="{{ item }}", update_cache="yes")),
                 #   with_items=["iptraf-ng"], action=dict(nsible_distribution="Debian"),
 
                 #dict(name="Check whether the package is installed or not", action=dict(module="yum", args=dict(name="{{ item }}", update_cache="yes")),
                  #   with_items=["iptraf-ng"], when=["ansible_distribution = 'Centos'"]),
 
                 dict(name="Copy and Execute the script", script="/root/script.sh", register="result", ignore_errors="yes", args=dict( executable="/bin/bash")),
                 #dict(name="Execute iptraf-ng", action=dict(module="command", args="sh script.sh"), register="result"),
 
                 dict(action=dict(module='debug', args=dict(msg='{{result.stdout_lines}}'))),
 
                 dict(name="clear the list file", local_action=dict(module="shell", args="true > /root/list")),
 
                 dict(name="copying the files", local_action=dict(module="lineinfile",
                     args=dict(line="{{result.stdout_lines}}", dest="/root/list")))]
 
 
        )
play = Play().load(play_src, variable_manager=variable_manager, loader=loader)
 
#actually run it
tqm = None
try:
    tqm = TaskQueueManager(
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            options=options,
            passwords=passwords,
            stdout_callback="default",
        )
    result = tqm.run(play)
finally:
    if tqm is not None:
        tqm.cleanup()