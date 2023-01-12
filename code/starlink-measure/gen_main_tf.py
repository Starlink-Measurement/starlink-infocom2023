#!/usr/bin/env python3
# Should only be run by shell script
import sys
import json
import argparse

KEY_MODULE = 'module'
KEY_OUTPUT = 'output'
KEY_PUBLIC_IP = 'public_ip'
KEY_REGION_NAME = 'region_name'

def main(args):
    main_config = {}

    main_config[KEY_MODULE] = []
    main_config[KEY_OUTPUT] = []
    for region in args.regions:
        region_dict = {}
        region_dict[region] = {}
        region_dict[region]['source'] = './modules/inst'
        region_dict[region]['region'] = region
        if region == 'me-south-1':
            region_dict[region]['instance_type'] = args.me_instance_type

        main_config[KEY_MODULE].append(region_dict)

        val_dict = {}
        val_dict[f'{region}_{KEY_PUBLIC_IP}'] = {}
        val_dict[f'{region}_{KEY_PUBLIC_IP}']['value'] = f"${{{KEY_MODULE}.{region}.{KEY_PUBLIC_IP}}}"
        val_dict[f'{region}_{KEY_REGION_NAME}'] = {}
        val_dict[f'{region}_{KEY_REGION_NAME}']['value'] = f"${{{KEY_MODULE}.{region}.{KEY_REGION_NAME}}}"
        main_config[KEY_OUTPUT].append(val_dict)

    main_config_json = json.dumps(main_config, indent=2)
    with open('./instances/main.tf.json', 'w') as out:
        out.write(main_config_json)

    print(f'Written terraform config with regions {args.regions}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate main terraform JSON config.')
    parser.add_argument('-me', '--me-instance-type', default='t3.micro', help='Instance type for region me-south-1, since they do not have t3.nano. Default: t3.micro')
    parser.add_argument('regions', nargs='+', help='Regions to spin up')

    args = parser.parse_args()
    main(args)
