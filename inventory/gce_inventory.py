#!/usr/bin/env python3

import json
import os
import subprocess

gcloud_completed_process = subprocess.run(
    ['gcloud', 'compute', 'instances', 'list', '--format', 'json'],
    check=True,
    stdout=subprocess.PIPE
)

gce_instances = json.loads(gcloud_completed_process.stdout.decode('utf-8'))

inventory = {
    '_meta': {
        'hostvars': {}
    },
    'all': {
        'hosts': [],
        'children': [
            'ungrouped'
        ]
    },
    'ungrouped': []
}

for instance in gce_instances:
    # pull hostvars out of instance
    hostvars = {}
    hostvars['zone'] = os.path.basename(instance['zone'])

    # add hostvars to _meta.hostvars
    inventory['_meta']['hostvars'][instance['name']] = hostvars

    # add instance to all group
    inventory['all']['hosts'].append(instance['name'])

    # add the instance to a service label group
    if 'labels' in instance and 'service' in instance['labels']:
        service = instance['labels']['service']
        inventory[service] = inventory.get(service, [])
        inventory[service].append(instance['name'])
        
        if service not in inventory['all']['children']:
            inventory['all']['children'].append(service)

    # add the instance to any additional label groups
    if 'labels' in instance and 'groups' in instance['labels']:
        groups = instance['labels']['service'].split(',')
        for group in groups:
            inventory[group] = inventory.get(group, [])
            inventory[group].append(instance['name'])
            
            if group not in inventory['all']['children']:
                inventory['all']['children'].append(group)

print(json.dumps(inventory))
