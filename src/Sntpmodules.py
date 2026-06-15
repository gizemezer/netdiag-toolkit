import socket
import struct
import sys
import time


NTP_SERVER = "0.uk.pool.ntp.org"# NTP server address
TIME1970 = 2208988800

def sntp_client():

    # time_local = time.time()#local time

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = b'\x1b' + 47 * b'\0' #create NTP request packet
    #Send request to NTP server.Port 123: NTP's standard port
    client.sendto(data, (NTP_SERVER, 123))

    data, address = client.recvfrom( 1024 )

    time_ntp = struct.unpack( '!12I', data )[10]# Parse NTP response packet
    time_ntp -= TIME1970 # Convert NTP time to Unix time

    ntp_server_time= time.ctime(time_ntp)
    # local_time = time.ctime(time_local)
    #Burayı yorum satırına aldım . yaparken karşılaştırmyaı görmek istedim ama arayüzde kullanmadım o yüzden de yoruma aldım
    #
    # difference = abs(time_ntp - time_local)

    # print(f"NTP Sunucu Zamanı: {ntp_server_time}")
    # print(f"Yerel Sistem Zamanı: {local_time}")
    # print(f"Fark: {difference:.3f} saniye")

    return ntp_server_time
