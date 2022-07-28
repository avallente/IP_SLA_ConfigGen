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