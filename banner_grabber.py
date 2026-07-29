import socket
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from ipaddress import ip_address
import ssl

def scan_and_grab(ip, start, end):
    port_map = {}
    lock = Lock()
    SSL_PORTS = {443, 465, 993, 995, 8443}

    def start_grabber(port):
        nonlocal ip
        banner = ""
        try:
            service = socket.getservbyport(port)
        except OSError:
            service = None

        s = socket.socket()
        s.settimeout(1)
        try:
            s.connect((ip, port))
            if port in SSL_PORTS:
                context = ssl.create_default_context()
                ssl_s = context.wrap_socket(s, server_hostname=ip)
                ssl_s.do_handshake()
                ssl_s.send(b"HEAD / HTTP/1.1\r\nHost: " + ip.encode() + b"\r\nConnection: close\r\n\r\n")
                banner = ssl_s.recv(1024).decode(errors="ignore")
                ssl_s.close()
            else:
                if port ==  80:
                    s.send(b"HEAD / HTTP/1.0\r\nHost: " + ip.encode() + b"\r\n\r\n")
                banner = s.recv(1024)
                if not banner:
                    s.send(b"\r\n")
                    banner = s.recv(1024)
                banner = banner.decode(errors="ignore")
        except Exception as e:
            pass
        finally:
            with lock:
                if banner:
                    port_map[port] = [banner, service]
            s.close()

    with ThreadPoolExecutor(max_workers=100) as exe:
        try:
            exe.map(start_grabber, range(start, end+1))
        except KeyboardInterrupt:
            print("Interrupt recieved!\nShutting down the client.")
            exe.shutdown(wait=False, cancel_futures=True)
    return port_map

def validate_ip(ip):
    try:
        ip_address(ip)
    except ValueError:
        try:
            socket.gethostbyname(ip)
        except socket.gaierror:
            print("\nIp address is not in the correct format.\nPlease enter the address again.")
            exit(0)

def format_banner(banners):
    output = []
    for i in banners:
        first_line = banners[i][0].splitlines()[0]
        server_line = next((line for line in banners[i][0].splitlines() if line.startswith("Server:")), "")
        service_line = banners[i][1]
        temp = f"{i} ({service_line}): {first_line}"
        if server_line:
            temp += f" | {server_line}"
        output.append(temp)
    return output
    

if __name__ == "__main__":
    ip_addr = input("Enter target address: ")
    validate_ip(ip_addr)
    start = int(input("Enter start port: "))
    end = int(input("Enter end port: "))
    while start>end:
        print("Starting mode must be less than ending port.")
        start = int(input("Enter start port: "))
        end = int(input("Enter end port: "))

    banners = scan_and_grab(ip=ip_addr, start=start, end=end)
    if banners:
        banners = format_banner(banners)
        for i in banners:
            print(i)
    else:
        print("No open ports")
