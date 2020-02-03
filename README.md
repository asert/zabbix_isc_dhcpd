Based on: https://github.com/jpmenil/zabbix-templates/isc-dhcp and https://github.com/garbled1/zabbix_isc_dhcpd


## Installation
# on dhcp server
* install dependencies:
    * pip install pypureomapi
    * pip install netaddr
* mv userparameter_dhcp.conf /etc/zabbix/zabbix_agentd.d/
* mv check_dhcp_leases.py /usr/local/bin/
* Add lines like #= NAME =# to the end of all range statements, if you want.
* edit check_dhcp_leases.py to fix your omapi key and key name, also, probably the location of your dhcpd.conf file.

# on zabbix server
* import templates in zabbix

# Fix at original version
* Fix graphs name - I changed it to ip rate. It's more useful for me and protect from duplicate.
* Add support config dir conf.d
* Zabbix 4.x.x - tested from Zabbix 4.0.0 to Zabbix 4.4.5
