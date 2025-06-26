import datetime
import yaml
class Logger:

    def __init__(self):
        self.protocol = {}
        self.results = {
            'General': {
                'Tests': 0,
                'Successful': 0,
                'Failed': 0,
                'Points reached': 0,
                'Points possible': 0,
                'Errors': []
            },
            'Criteria': []
        }

    def add_error(self, errors):
        self.results['General']['Errors'].extend(errors['list'])
        self.protocol.setdefault(errors['tag'],errors['err'])

    def add_event(self, events:list, name):

        for event in events:
            self.protocol.setdefault(name, [])
            self.protocol[name].append(event)

    def add_test_event(self, events:list, points, testcase):
        
        #update Protocol
        for event in events:
            event.setdefault('Executing Machine', testcase.source)
            event['TestNr'] = event['TestNr'] + self.results['General']['Tests']
            self.protocol.setdefault(testcase.name, [])
            self.protocol[testcase.name].append(event)

        #update Criteria category
        self.results['Criteria'].append({testcase.name:{
            'Points reached': points,
            'Points possible': testcase.points
        }})

        # update general category
        self.results['General']['Points reached'] += points
        self.results['General']['Failed'] += len(events) - ((points/testcase.points) * len(events))
        self.results['General']['Successful'] += (points/testcase.points) * len(events)
        self.results['General']['Points possible'] += testcase.points
        self.results['General']['Tests'] += len(events)

    def write(self, path_dir=None, path_res=None, path_proto=None):
        timestamp = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
        if path_proto is None:
            path_proto = f"{path_dir}/ant-protocol-{timestamp}.yml"
        if path_res is None:
            path_res = f"{path_dir}/ant-results-{timestamp}.yml"

        with open(path_res, 'w', encoding='utf-8') as results_file:
            yaml.dump(self.results, results_file)

        with open(path_proto, 'w', encoding='utf-8') as protocol_file:
            yaml.dump(self.protocol, protocol_file)

        return self.results['General']
