import shutil
from ant_backend import AnsibleManager, NetworkConfiguration, TestcaseConfiguration
import ansible_runner

if __name__ == '__main__':
    manager = AnsibleManager('template_mapping.yml')
    netconfig = NetworkConfiguration()
    testcases = TestcaseConfiguration()

    netconfig.load_from_yaml('test_infra.yml')
    testcases.load_from_yaml('tests.yml')

    '''manager.create_inventory('ansible_runner/inventory/inventory.yml', netconfig, testcases)

    runner = ansible_runner.run(private_data_dir="ansible_runner", playbook="icmp_playbook.yml", quiet=True)

    return_dict = {}

    for event in runner.events:
        if event['event'] == 'runner_item_on_ok' or event['event'] == 'runner_item_on_failed':
            data = event.get('event_data', {})
            res = data.get('res', {})
            return_dict[data.get('host')] = {k: res.get(k) for k in ('stdout', 'stderr', 'rc', 'cmd', 'start', 'end', 'delta', 'msg')}
            return_dict[data.get('host')]['unreachable'] =  res.get('unreachable', False)

    print(return_dict)
    shutil.rmtree("ansible_runner/artifacts")'''

    manager.create_nft_inventory('ansible_runner/inventory/setup.yml', netconfig)

    manager.execute_playbook('setup.yml')
