#!/usr/bin/python -u
# -*- coding: utf-8 -*-

from google.cloud import dns
from google.cloud.exceptions import NotFound
import os
import time
import ipgetter

config = {
    'project_id': os.environ.get('PROJECT_ID'),
    'zone_name': os.environ.get('DNS_ZONE_NAME'),
    'dns_name': os.environ.get('DNS_NAME'),
    'refresh_interval': int(os.getenv('DNS_REFRESH_INTERVAL', '300')),
    'record_ttl': int(os.getenv('DNS_RECORD_TTL', '300')),
    'record_type': os.getenv('DNS_RECORD_TYPE', 'A'),
}


if config['project_id'] is None: raise SystemExit('PROJECT_ID needs to be set')
if config['zone_name'] is None: raise SystemExit('DNS_ZONE_NAME needs to be set')
if config['dns_name'] is None: raise SystemExit('DNS_NAME needs to be set')

def create_zone():
    client = dns.Client(project=config['project_id'])
    zone = client.zone(config['zone_name'], config['dns_name'], description='Created by rpi-google-cloud-dynamic-dns')

    if not zone.exists():  # API request
        zone.create()  # API request
        while not zone(exists):
            print('Waiting for creation of domain ' + config['dns_name'] + ' in zone ' + config['zone_name'] + ' to complete')
            time.sleep(10)     # or whatever interval is appropriate

def update_domain():
    client = dns.Client(project=config['project_id'])
    zone = client.zone(config['zone_name'], config['dns_name'])

    ip = ipgetter.myip();

    changes = zone.changes()


    records = zone.list_resource_record_sets()
    for record in records:
        if record.name == config['dns_name']:
            if record.record_type == config['record_type'] and record.ttl == config['record_ttl'] and record.rrdatas[0] == ip:
                #no update needed
                print('No update needed for ' + config['dns_name'] + ' in zone ' + config['zone_name'] + ' rrdata: ' + record.rrdatas[0])
                return
            else:
                #delete out of date record bfore adding new
                print('Delete out of date record set ' + config['dns_name'] + ' in zone ' + config['zone_name'] + ' rrdata: ' + record.rrdatas[0])
                record_delete = zone.resource_record_set(record.name, record.record_type, record.ttl, record.rrdatas)
                changes.delete_record_set(record_delete)
            break

    print('Add record set ' + config['dns_name'] + ' in zone ' + config['zone_name'] + ' rrdata: ' + ip)
    record_set = zone.resource_record_set(config['dns_name'], config['record_type'], config['record_ttl'], [ip,])
    changes.add_record_set(record_set)
    changes.create()  # API request
    while changes.status != 'done':
        print('Waiting for changes for ' + config['dns_name'] + ' in zone ' + config['zone_name'] + ' rrdata: ' + ip)
        time.sleep(10)     # or whatever interval is appropriate
        changes.reload()   # API request
    print('Change ' + config['dns_name'] + ' in zone ' + config['zone_name'] + ' rrdata: ' + ip + ' updated')

if __name__ == '__main__':
    create_zone()
    while True:
        update_domain()
        time.sleep(config['refresh_interval'])
