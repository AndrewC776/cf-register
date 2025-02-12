import requests
import yaml

# 2024-08-10 BRG365.

# GoDaddy API
api_key = 'your_api_key' 
api_secret = 'your_api_secret'

# API header
headers = {
    'Authorization': f'sso-key {api_key}:{api_secret}',
    'Content-Type': 'application/json'
}


# Cloudflare dns
nameservers = ['gloria.ns.cloudflare.com', 'pranab.ns.cloudflare.com']


def sync_online_dns_records(config_file_path='config_dns_records.yaml'):
    data = yaml.safe_load(open(config_file_path))
    for item in data:
        records = item.get('records', [])
        for record in records:
            domain = record.get('name')
            data = {
                "nameServers": nameservers
            }
            response = requests.patch(f'https://api.godaddy.com/v1/domains/{domain}', headers=headers, json=data)
            if response.status_code == 200:
                print(f'{domain} updated successfully!')
            else:
                print(f'Failed to update {domain}: {response.text}')
