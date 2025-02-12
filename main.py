import os
import time
import requests
import yaml

# 2024-08-10 brg365.
# Replace to you Cloudflare API Token
api_token = 'xf'
account_id = 'ff'
# online conf
online_dns_records_yaml = 'online_dns_records.yaml'
# local conf
config_dns_records_yaml = 'config_dns_records.yaml'

headers = {
    'Authorization': f'Bearer {api_token}',
    'Content-Type': 'application/json',
}


def get_account_id():
    # Cloudflare API endpoint URL
    url = 'https://api.cloudflare.com/client/v4/user'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            account_id = data['result']['id']
            print(f'Cloudflare Account ID: {account_id}')
        else:
            print(f'Error: {data.get("errors")}')
    else:
        print(f'HTTP Error: {response.status_code}')
        print(f'Response Content: {response.text}')


def get_all_domains():
    records = []
    page = 1
    per_page = 100
    total_pages = 1
    url = 'https://api.cloudflare.com/client/v4/zones'
    while page <= total_pages:
        params = {
            'per_page': per_page,
            'page': page
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # 检查 HTTP 响应状态码是否为 200
        result = response.json()

        if result.get('success'):
            zones = result.get('result', [])
            for zone in zones:
                print(zone)
                record = query_dns_records(zone['id'], zone['name'])
                records.append(record)

            result_info = result.get('result_info', {})
            total_pages = result_info.get('total_pages', 1)
            page += 1
        else:
            print(f'Error fetching DNS records: {result.get("errors")}')
            break
    return records


def query_dns_records_type(zone_id, name, record_type):
    """根据 zone_id 和记录名称查询 DNS 记录"""
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?name={name}&type={record_type}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        result = response.json()
        records = result.get('result', [])
        return records
    else:
        print(f'Error querying DNS records: {response.status_code}')
    return []


def query_dns_records(zone_id, domain_name):
    records_url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
    records = {'name': domain_name, 'records': [{'type': 'A', 'name': '@', 'content': '127.0.0.1'},
                                                {'type': 'CNAME', 'name': 'www', 'content': '@'}]}
    params = {
        'per_page': 100,
        'page': 1
    }
    try:
        time.sleep(1)
        response = requests.get(records_url, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
        if result.get('success'):
            datas = result.get('result', [])
            if len(datas) > 0:
                record_list = []
                for record in datas:
                    item = {
                        'name': record['name'],
                        'type': record['type'],
                        'content': record['content'],
                    }
                    record_list.append(item)
                records = {'name': domain_name, 'records': record_list}
        else:
            print(f'Error fetching DNS records: {result.get("errors")}')
    except requests.RequestException as e:
        print(f'HTTP Request failed: {e}')
    return records


def query_zone(domain_name):
    url = f'https://api.cloudflare.com/client/v4/zones?name={domain_name}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            zones = data['result']
            if zones:
                zone = zones[0]
                print(f"Zone ID: {zone['id']}, Name: {zone['name']}")
                return  zone
            else:
                print(f"No zone found for domain: {domain_name}")
        else:
            print(f'Error: {data.get("errors")}')
    else:
        print(f'HTTP Error: {response.status_code}')
        print(f'Response Content: {response.text}')


def update_dns_record(record_type, name, content, proxied=True):
    zone = query_zone(domain_name=name)
    if zone:
        zone_id = zone['id']
        # exit recored
        online_record = query_dns_records_type(zone_id=zone_id, name=name, record_type=record_type)
        data = {
            'type': record_type,
            'name': name,
            'content': content,
            'proxied': proxied,  
            'ttl': 3600  # TTL
        }
        if online_record:
            # update recored
            record_id = online_record[0]['id']
            url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}'
            response = requests.put(url, headers=headers, json=data)
        else:
            url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
            response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"{record_type} record created successfully for {name}!")
            else:
                print(f'Error creating {record_type} record for {name}: {result.get("errors")}')
        else:
            print(f'HTTP Error: {response.status_code}')
            print(f'Response Content: {response.text}')
    else:
        print('No zone found for domain')


def download_account_dns_records():
    try:
        records = get_all_domains()
        with open(online_dns_records_yaml, 'w', encoding='utf-8') as file:
            yaml.dump(records, file, default_flow_style=False, allow_unicode=True)
    except requests.RequestException as e:
        print(f'HTTP Request failed: {e}')

    except Exception as e:
        print(f'An unexpected error occurred: {e}')


def sync_online_dns_records():
    data = yaml.safe_load(open(config_dns_records_yaml, 'r', encoding='utf-8'))
    if isinstance(data, list) and all(isinstance(item, dict) and 'name' in item and 'records' in item for item in data):
        print("begin update...")
    else:
        print("YAML proxy error...")
        return
    for item in data:
        records = item.get('records', [])
        for record in records:
            record_type = record.get('type')
            name = record.get('name')
            content = record.get('content')

            if not record_type or not name or not content:
                print(f'Missing required fields in record: {record}')
                continue

            if record_type not in ['A', 'AAAA', 'TXT', 'CNAME']:
                print(f'Unsupported record type: {record_type}')
                continue

            update_dns_record(record_type, name, content)


def main():
    # 1.donwload all domain config build online_dns_records.yaml
    if os.path.exists(online_dns_records_yaml) and os.path.exists(config_dns_records_yaml):
        sync_online_dns_records()
    else:
        download_account_dns_records()


if __name__ == "__main__":
    main()