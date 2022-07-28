import os
import orionsdk
from jinja2 import FileSystemLoader, PackageLoader, Template, Environment, select_autoescape

'''
Welcome to my IP SLA generator for ICMP-ECHOs.
This was written because we want to monitor the circuit status of some couple hundred
circuits, and writing that out by hand would simply be unmaintainable and quite boring,
enter this script! This is acutally the second version of a script that I had previously
written, but this uses Jinja2 for the formatting, and directly makes a call to the Orion
DB, whereas previously you would need to manually write a query, format it, and feed it
to the program.

Here's an overview of how to read the IP SLA operation IDs, which is what the bulk of
what this script was written to handle.

The Operation ID (OID) is made of four parts:
•   The device ID; derived from the last two octects of the device loopback address
•   The index of the circuit on the device; most sites have 2+ circuits and therefore
    operations
•   The SLA type; there are 14 supported SLA types on cisco devices (even though this
    script deals with icmp for now, I'm including space in the naming scheme for expansion)

These parts come together to make an 7 digit OID.
Device ID | Circuit Number | SLA Type
   XXXX   .       X        .    XX

IPSLA Types

1: ftp
2: http
3: icmp-echo
4: icmp-jitter
5: path-echo
6: path-jitter
7: tcp-connect
8: udp-echo
9: udp-jitter
10: dhcp
11: dns
12: ethernet-echo
13: ethernet-jitter
14: ethernet-y1731
'''

def generate_DID(query_list):
    # Identify duplicate Site IDs and add appropriate index
    for i in range(len(query_list)):
        duplicate_count = 0
        x = 0
        while query_list[i-x]['SID'] == query_list[i-x-1]['SID']:
            x += 1
            duplicate_count += 1
        query_list[i]['DID'] = query_list[i]['SID'] + str(duplicate_count)

def generate_OID(query_list, operation_type):
    while len(str(operation_type)) < 2:
        operation_type = '0' + str(operation_type)
    for row in query_list:
        row['OID'] = row['DID'] + str(operation_type)


def main():
    # Initialize connection to orion server
    swis = orionsdk.SwisClient("txlphqsorion1.usdom1.ad", "admin", "C1sco123!")

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

    generate_DID(wan_node_query_list)
    generate_OID(wan_node_query_list, 3)

    try:
        os.remove('outputs/ipsla_config.txt')
    except:
        None

    # Generate configuration
    for row in wan_node_query_list:
        data = {
            'operation_number': row['OID'],
            'destination_address': row['Target Address'],
            'tag_text': row['tag']
        }
        with open('outputs/ipsla_config.txt', 'a') as f:
            f.write(j2_template.render(data))

if __name__ == '__main__':
    main()