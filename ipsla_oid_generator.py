import os
import json
import orionsdk
from jinja2 import FileSystemLoader, PackageLoader, Template, Environment, select_autoescape

def generate_DID(query_list):
    # Identify duplicate Site IDs and add appropriate index
    for i in range(len(query_list)):
        duplicate_count = 0
        x = 0
        while query_list[i-x]['SID'] == query_list[i-x-1]['SID']: # Lookback for duplicates
            x += 1
            duplicate_count += 1
        query_list[i]['DID'] = query_list[i]['SID'] + str(duplicate_count)

def generate_OID(query_list, operation_type):
    generate_DID(query_list)
    while len(str(operation_type)) < 2:
        operation_type = '0' + str(operation_type)
    for row in query_list:
        row['OID'] = row['DID'] + str(operation_type)


def main():
    # Grab creds
    credential = json.loads((open('private/mymomsenchiladarecipe.json', 'r')).read())

    # Initialize connection to orion server
    swis = orionsdk.SwisClient(credential['orionDB']['hostname'], 
                               credential['orionDB']['username'],
                               credential['orionDB']['password'])

    # Initialize Jinja2 env
    env = Environment(
        loader=FileSystemLoader('./templates'),
        autoescape=select_autoescape(),
        keep_trailing_newline=True
    )

    # Create query
    wan_node_query = swis.query(open('orion_query.txt', 'r').read())

    # Create list of rows
    wan_node_query_list = wan_node_query['results']

    # Open Jinja2 template
    #ip_sla_config_template = (open('templates/cisco_configure_icmp_ipsla.j2', 'r').read())
    j2_template = env.get_template('cisco_configure_icmp_ipsla.j2')

    # Generate the IP SLA operation ID
    generate_OID(wan_node_query_list, 3)

    # Destroy previous config file
    try:
        os.remove('outputs/ipsla_config.txt')
    except:
        None

    # Generate configuration
    for row in wan_node_query_list: # Iterate through queries
        # Create data dict to feed to Jinja
        data = {
            'operation_number': row['OID'],
            'destination_address': row['Target Address'],
            'tag_text': row['tag']
        }
        with open('outputs/ipsla_config.txt', 'a') as f:
            f.write(j2_template.render(data)) # Feed data to Jinja template and print to txt file

if __name__ == '__main__':
    main()