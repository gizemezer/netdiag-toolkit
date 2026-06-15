import socket
from ErrSet import write_log, settings, load, apply # Functions from custom module

data_payload = 2048 # Maximum data size (bytes)
backlog = 5 #Pending connection queue size


def echo_server(host, port, callback=None):
    load() #Load settings
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# Create IPv4, TCP socket
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_address = (host, port)
    message_bytes = "Umarım yüksek alırım".encode('utf-8')

    def log(msg):
        #to manage log messages
        if callback:
            callback(msg)
        print(msg)
        if settings.get("enable_logging", True):
            write_log(msg)

    try:
        sock.bind(server_address)
        apply(sock)# Apply custom socket settings (from ErrSet module)
        sock.listen(backlog)

        log(f" Sunucu başlatıldı: {host}:{port}")
        log(" Client bağlantısı bekleniyor...")

        client, address = sock.accept() # Accept client connection
        log(f"Client bağlandı: {address}")

        data = client.recv(data_payload)


        if data:
            # Compare received data with expected message
            if data == message_bytes:
                comparison_status = "Başarılı aferin be"
            else:
                comparison_status = "Veri eşlenmedi"

            log(f"Alınan Veri: {data.decode('utf-8')} ({comparison_status})")

            client.sendall(data)
            result_status = f"Sunucu Başarılı: {len(data)} byte veri alındı, kontrol edildi ve geri gönderildi. ({comparison_status})"
            log(result_status)
        else:
            result_status = "Sunucu Başarılı: Bağlantı kuruldu ancak veri alınmadı."
            log(result_status)
    except socket.error as e:
        result_status = f"Sunucu Hatası: {str(e)}"
        log(result_status)
    except Exception as e:
        result_status = f"Genel Hata: {str(e)}"
        log(result_status)
    finally:
        # Bağlantı ve ana soketi kapat
        if 'client' in locals() and client:
            client.close()
        sock.close()
        log("Sunucu soketi kapatıldı. (İşlem tamamlandı)")
        return result_status




def echo_client(host, port, callback=None):
    load()# Load settings
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (host, port)


    sock.connect(server_address)#Connect to server
    apply(sock)

    def log(msg):
        if callback:
            callback(msg)
        print(msg)
        if settings.get("enable_logging", True):
            write_log(msg)
    try:
        log(f"Connecting to {host}:{port}")
        message = "Umarım yüksek alırım"
        log("Sending %s" % message)
        sock.sendall(message.encode('utf-8'))

        amount_received = 0
        amount_expected = len(message)#Expected total data size
        full_received_data = b''
        #Loop until all data is received
        while amount_received < amount_expected:
            data = sock.recv(16)

            full_received_data += data
            amount_received += len(data)

       #Encode message with UTF-8 and send to server
        received_message = full_received_data.decode('utf-8')
        log("Received: %s" % received_message)
        # Compare sent and received message
        if received_message == message:
            result = "İşlem tamam her şey yolunda."
            log(result)
        else:
            result = f"Hata: eşleşmedi . Gönderilen: {message}, Alınan: {received_message}"
            log(result)

    except socket.error as e:
        log("Socket error: %s" % str(e))
    except Exception as e:
        log("Other exception: %s" % str(e))
    finally:
        log("Closing connection to the server")
    sock.close()
    return result
