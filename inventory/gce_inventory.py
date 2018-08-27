#!/usr/bin/env python3

import json
import os
import pprint
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

    for tag in instance['tags']['items']:
        group_name = 'tag_' + tag

        # add instance to tag group
        inventory[group_name] = inventory.get(group_name, [])
        inventory[group_name].append(instance['name'])

        # add tag group to all group
        if group_name not in inventory['all']['children']:
            inventory['all']['children'].append(group_name)

print(json.dumps(inventory))
