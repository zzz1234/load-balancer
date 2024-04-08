import socket
import threading
import signal
import sys
import argparse
import time

backend_sockets = []


class LoadBalancer:
    def __init__(self, backend_servers, health_check_interval):
        self.backend_servers = [(x.split(":")[0], int(x.split(":")[1])) for x in backend_servers]
        self.healthy_servers =  [(x.split(":")[0], int(x.split(":")[1])) for x in backend_servers]
        self.request_count = 0
        self.health_check_interval = health_check_interval
        self.lb_socket = self.create_lb_socket()
    
    def create_lb_socket(self):
        lb_host = '127.0.0.1'
        lb_port = 80
        lb_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lb_socket.bind((lb_host, lb_port))
        lb_socket.listen(5)
        print(f"Load balancer listening on {lb_host}:{lb_port}")
        return lb_socket

    def handle_interrupt(self, signum, frame):
        print("Received Ctrl + C. Exiting gracefully.")
        # Clean up resources (e.g., close sockets)
        for backend_socket in backend_sockets:
            backend_socket.close() 
        sys.exit(0)

    def handle_client(self, client_socket):
        backend_response = self.forward_to_backend(client_socket)
        client_socket.sendall(backend_response)
        client_socket.close()
        # return backend_response
    
    def forward_to_backend(self, client_socket):
        backend_host, backend_port = self.healthy_servers[self.request_count % len(self.healthy_servers)]
        self.request_count += 1
        backend_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend_socket.connect((backend_host, backend_port))
        client_request = client_socket.recv(4096)
        backend_socket.sendall(client_request)

        # Receive the backend response
        backend_response = b''
        while True:
            data = backend_socket.recv(4096)
            if not data:
                break
            backend_response += data

        backend_socket.close()
        return backend_response
    
    def health_check(self, server_index):
        while True:
            backend_host, backend_port = self.backend_servers[server_index]
            
            # Perform health check on the server
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(2)  # Timeout for the health check
                    s.connect((backend_host, backend_port))
                    if self.backend_servers[server_index] not in self.healthy_servers:
                        self.healthy_servers.append(self.backend_servers[server_index])
                        print(f"Health check passed for {backend_host}:{backend_port}")
                    s.close()
            except Exception as e:
                print(f"Health check failed for {backend_host}:{backend_port}: {e}")
                if self.backend_servers[server_index] in self.healthy_servers:
                    self.healthy_servers.remove(self.backend_servers[server_index])
            
            time.sleep(self.health_check_interval)  # Health check interval


def get_arguments():
    parser = argparse.ArgumentParser(description='Load balancer')
    parser.add_argument('--backend-servers', nargs='+', type=str, default=['127.0.0.1:8080', '127.0.0.1:8081', '127.0.0.1:8082'])
    parser.add_argument('--health-check-interval', type=int, default=5)
    args = parser.parse_args()
    return args


def health_check_servers(lb):
    health_check_threads = []
    for i in range(len(lb.backend_servers)):
        t = threading.Thread(target=lb.health_check, args=(i,))
        t.daemon = True  # Health check threads will exit when the main thread exits
        t.start()
        health_check_threads.append(t)


def main():
    args = get_arguments()
    lb = LoadBalancer(args.backend_servers, args.health_check_interval)
    health_check_servers(lb)

    signal.signal(signal.SIGINT, lb.handle_interrupt)

    while True:
        client_socket, client_address = lb.lb_socket.accept()
        print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
        
        client_thread = threading.Thread(target=lb.handle_client, args=(client_socket,))
        client_thread.start()
        # handle_client(client_socket)

if __name__ == '__main__':
    main()
