# rack_em is a python HTTP server created with a socket server

import argparse
import socket
import threading


# request data is parsed
def find_data_in_req(data):
    info = data.split("\r\n")
    begin = info[0]
    func, loc, v = begin.split(" ")
    headers = {}
    for line in info[1:]:
        if line == "":
            break
        h, v = line.split(": ", 1)
        headers[h] = v

    return func, loc, v, headers


# get the server response
def get_resp(state, type, body):
    headers = [
        f"HTTP/1.1 {state}",
        f"Content-Type: {type}",
        f"Content-Length: {len(body)}",
        "",
        body,
    ]
    default = "\r\n".join(headers)
    return default


# handler for the request
def handle_req(socket):
    try:
        data = socket.recv(1024).decode()
        if not data:
            return

        _, path, _, headers = find_data_in_req(data)
        if path == "/":
            receive = get_resp("200 OK", "text/plain", "")
        elif path.startswith("/echo/"):
            string = path.split("/echo/")[1]
            receive = get_resp("200 OK", "text/plain", string)
        elif path == "/user-agent":
            ua = headers.get("User-Agent", "Unknown")
            receive = get_resp("200 OK", "text/plain", ua)
        else:
            receive = get_resp("404 Not Found", "text/plain", "")

        socket.send(receive.encode())
    finally:
        socket.close()


def worker(connection, address):
    print(f"working on {address} ... for the robots ...")
    handle_req(connection)


# server application
def main():
    parser = argparse.ArgumentParser(description="Test File For Robots.")
    parser.add_argument("--directory", type=str, help="Directory")
    args = parser.parse_args()
    global base_directory
    base_directory = args.directory

    server = socket.create_server(("localhost", 4221), reuse_port=True)
    server.listen()
    print("SERVER UP, PORT 4221")

    try:
        while True:
            print("Patiently Waiting For Connection!")
            conn, loc = server.accept()
            t = threading.Thread(target=worker, args=(conn, loc))
            t.start()
    except KeyboardInterrupt:
        print("\nServer going going going ...")
    finally:
        server.close()
        print("Server down down down ...")


if __name__ == "__main__":
    main()
