#!/usr/bin/python2
"""Usage:
    pymoticz list [--host]
    pymoticz test
    pymoticz status <id> [--host]
    pymoticz on <id> [--host]
    pymoticz off <id> [--host]
    pymoticz dim <id> <level> [--host]
"""
import requests
import json

__all__ = [ 'Pymoticz' ]
__version__ = '0.1'

class Pymoticz:
    DIMMER = u'Dimmer'
    ON_OFF = u'On/Off'
    SWITCH_TYPES=[ DIMMER, ON_OFF ]
    def __init__(self, domoticz_host='127.0.0.1:8080'):
        self.host = domoticz_host

    def _request(self, url):
        r=requests.get(url)

        if r.status_code == 200:
            return json.loads(r.text)
        else:
            raise

    def list(self):
        url='http://%s/json.htm?type=devices&used=true' % self.host
        return self._request(url)

    def turn_on(self, _id):
        url='http://%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=On' % (self.host, _id)
        return self._request(url)

    def turn_off(self, _id):
        url='http://%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=Off&level=0' % (self.host, _id)
        return self._request(url)

    def dim(self, _id, level):
        max_dim=self.get_device(_id)['MaxDimLevel']
        if int(level) > max_dim or int(level) < 0:
            return 'Level has to be in the range 0 to %d' % max_dim
        url='http://%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=Set Level&level=%s' % (self.host, _id, level)
        return self._request(url)

    def get_device(self, _id):
        l=self.list()
        device=[i for i in l['result'] if i['idx'] == u'%s' % _id][0]
        return device

    def get_light_status(self, _id):
        light = self.get_device(_id)
        if light is None:
            return 'No device with that id.'
        if light['SwitchType'] not in self.SWITCH_TYPES:
            return 'Not a light switch'
        elif light['SwitchType'] == self.DIMMER:
            return light['Level']
        elif light['SwitchType'] == self.ON_OFF:
            return light['Status']

if __name__ == '__main__':
    from docopt import docopt
    from pprint import pprint
    args=docopt(__doc__, version=__version__)

    p=None
    if args['--host']:
        p=Pymoticz(args['--host'])
    else:
        p=Pymoticz()

    if args['list']:
        response = p.list()
        print(response)
    elif args['status']:
        response = p.get_light_status(args['<id>'])
        print(response)
    elif args['on']:
        response = p.turn_on(args['<id>'])
    elif args['off']:
        response = p.turn_off(args['<id>'])
    elif args['dim']:
        response = p.dim(args['<id>'], args['<level>'])
        pprint(response)
