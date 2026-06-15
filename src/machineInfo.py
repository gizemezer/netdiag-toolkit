import socket
import netifaces as ni #To get network interface info
import psutil #For system and process information


def print_machine_info():
    #to hostname and ıp address
    host_name = socket.gethostname()

    ip_address = socket.gethostbyname(host_name)
    return host_name,  ip_address


def extract_ipv6_info():
    #to netwrok interface and ıp addresses
    interfaces_info = []
    psutil_ifaces = psutil.net_if_addrs()

    # Loop through each network interface Try to get interface addresses with netifacesand psutil
    for interface in psutil_ifaces.keys():
        iface_data = {"interface": interface, "ips": []}

        try:
            all_addresses = ni.ifaddresses(interface)
        except Exception:

            addrs = psutil_ifaces.get(interface, [])
            # For each address add IP address to the list
            for addr in addrs:
                if addr.family in (socket.AF_INET, socket.AF_INET6):
                    iface_data["ips"].append(addr.address)
            if not iface_data["ips"]:
                iface_data["warning"] = "Bu arayüzde IP adresi yok"
            interfaces_info.append(iface_data)
            continue

        #  For each address family returned by netifaces add the cleaned IP address to the list
        for family, address in all_addresses.items():
            for addr in address:
                if family in [ni.AF_INET, ni.AF_INET6]:
                    addr_ = addr['addr']
                    if "%eth" in addr_:
                        addr_ = addr_.split("%eth")[0]
                    iface_data["ips"].append(addr_)

        if not iface_data["ips"]:
            iface_data["warning"] = "Bu arayüzde IP adresi yok"

        interfaces_info.append(iface_data)

    return interfaces_info


