from argparse import ArgumentParser, RawDescriptionHelpFormatter
import sys
import os
from ant_backend import AnsibleManager, Logger, NetworkConfiguration, TestcaseConfiguration, validate_script

BANNER = """
================================================================
                       d0000 000b    000 00000000000 
                      d00000 0000b   000     000     
                     d00P000 00000b  000     000     
                    d00P 000 000Y00b 000     000     
                   d00P  000 000 Y00b000     000     
                  d00P   000 000  Y00000     000     
                 d0000000000 000   Y0000     000     
                d00P     000 000    Y000     000 
=================================================================
                    Automated NFTables Tester
"""

def ant_main(config, net_config_path, testcases_path, verbose, dir, report, protocol):

    net_config = NetworkConfiguration()
    testcase_config = TestcaseConfiguration()
    logger = Logger()

    try:
        manager = AnsibleManager(config)
    except FileNotFoundError as e:
        msg = f"File {net_config_path} does not exist"
        print(msg)
        logger.add_error({'err': e, 'list': [msg], 'tag':'Netconfig'})
        if verbose:
            print(e)
        finalize(logger, 1, dir, report, protocol)

    if getattr(sys, 'frozen', False):
        tool_dir = os.path.dirname(sys.executable)
    else:
        tool_dir = f"{os.path.dirname(__file__)}/.."
    inventory_dir = f"{tool_dir}/ansible_runner/inventory"

    print(BANNER)

    print("Loading Network configuration...")
    try:
        net_config.load_from_yaml(net_config_path)
    except (AttributeError, ValueError) as e:
        msg = f"Error parsing network configuration {net_config_path}"
        print(msg)
        logger.add_error({'err': e, 'list': [msg], 'tag':'Netconfig'})
        if verbose:
            print(e)
        finalize(logger, 1, dir, report, protocol)
    except FileNotFoundError as e:
        msg = f"File {net_config_path} does not exist"
        print(msg)
        logger.add_error({'err': e, 'list': [msg], 'tag':'Netconfig'})
        if verbose:
            print(e)
        finalize(logger, 1, dir, report, protocol)

    print("Done.")

    print("Checking NFTable configuration files...")
    for _, machine in net_config.machines.items():
        if machine.nftable != '':
            errors, error = validate_script(machine.nftable)
            if errors:
                print(f"The script {machine.nftable} has invalid syntax.")
                logger.add_error({'err': error, 'list': errors, 'tag':'NFTables'})
                if verbose:
                    print(errors)
                finalize(logger, 1, dir, report, protocol)

    print("Done.")

    print("Loading Testcases...")
    try:
        testcase_config.load_from_yaml(testcases_path)
    except AttributeError as e:
        msg = "Error parsing testcases"
        logger.add_error({'err': e, 'list': [msg], 'tag':'Testcases'})
        if verbose:
            print(e)
        finalize(logger, 1, dir, report, protocol)
    except FileNotFoundError as e:
        msg = f"File {testcases_path} does not exist"
        print(msg)
        logger.add_error({'err': e, 'list': [msg], 'tag':'Netconfig'})
        if verbose:
            print(e)
        finalize(logger, 1, dir, report, protocol)
    print("Done.")

    try:
        print("Setting up firewalls...")
        manager.create_nft_inventory(f"{inventory_dir}/setup.yml", net_config)
        results = manager.execute_playbook("setup.yml")
    except TimeoutError as e:
        msg = "Error while setting up firewalls"
        logger.add_error({'err':e, 'list':[msg], 'tag':'Firewall setup'})
        print(msg)
        finalize(logger, 1, dir, report, protocol)

    for host, result in results.items():
        if result['unreachable']:
            logger.add_error({'err':result, 'list':[f"Fatal: {host.split('-')[1]} unreachable"],
                               'tag':host})
            finalize(logger, 1, dir, report, protocol)

        if result['rc'] != 0:
            logger.add_error({'err':result, 'list':["Fatal failure setting up " +
                                                    f"{host.split('-')[1]}"], 'tag':host})
            finalize(logger, 1, dir, report, protocol)

        logger.add_event([result], host)

    print("Setting up tests...")
    try:
        manager.create_inventory(f"{inventory_dir}/inventory.yml", net_config, testcase_config)
    except ValueError as e:
        msg = "Error while creating tests"
        print(msg)
        logger.add_error({'err':e, 'list':[msg], 'tag':'Testsetup'})

    print("Running tests...")
    results = manager.run()
    print("Done.")

    event_list = []
    points = 0

    for testcase in testcase_config.testcases:
        testnr = 0
        hostname = net_config.machines[testcase.source].name

        # get all events belonging to the testcase
        while True:
            event = f"{hostname}-{str(testcase.name)}-{testnr}"
            result = results.get(event, None)
            #check if all events have been handled
            if result is None:
                if len(event_list) == 0:
                    points = 0
                    break
                points = (points/len(event_list)) * testcase.points
                break

            event_list.append({'TestNr': testnr})
            event_list[testnr].update(result)

            #if event was successful increment points
            if result['rc'] == 0 and testcase.allow:
                points += 1
            elif not testcase.allow:
                points += 1

            testnr += 1

        logger.add_test_event(event_list, points, testcase)
        points = 0
        event_list = []

    finalize(logger, 0, dir, report, protocol)


def finalize(logger:Logger, rc, dir, report, protocol):
    output:dict = logger.write(dir, report, protocol)
    if rc == 0:
        print("Testing finished:")
    else:
        print("A fatal error occured: Exiting.")
    for key, item in output.items():
        print(f"{key}: {item}")
    sys.exit(rc)

if __name__ == '__main__':
    parser = ArgumentParser(
        prog="ant",
        description=BANNER,
        formatter_class=RawDescriptionHelpFormatter
    )

    parser.add_argument('-i', '--infrafile',
                        help='The path to the infrastructure configuration file', required=True)
    parser.add_argument('-t', '--testcases',
                        help='The path to the testcase configuration file', required=True)
    parser.add_argument('-c', '--config', default='mapping.yml',
                        help='path to the configuration file')
    parser.add_argument('-r', '--report', help='report file, overrides --dir option')
    parser.add_argument('-p', '--protocol', help='protocol file, overrides --dir option')
    parser.add_argument('-d', '--dir', default='.', help='output directory')
    parser.add_argument('-v', '--verbose', action='store_const', const=True, default=False)

    args = parser.parse_args()
    ant_main(args.config, args.infrafile, args.testcases, args.verbose, args.dir, args.report, args.protocol)
