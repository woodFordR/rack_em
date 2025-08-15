# rack_em is a python HTTP server created with a socket server

import argparse
import os
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
        http_req = socket.recv(1024).decode("utf-8")
        req_body = ""

        if not http_req:
            return
        else:
            header_end = http_req.find("\r\n\r\n")
            body_start = header_end + 4
            if header_end != -1 and body_start != -1:
                headers = http_req[:header_end]
                req_body = http_req[body_start:-1] + http_req[-1]
            else:
                headers = http_req[:header_end]

        crud, path, _, _ = find_data_in_req(http_req)

        if crud == "POST":
            if path.startswith("/files/"):
                file = path.split("/files/")[1]
                f_path = os.path.join(base_directory, file)
                os.makedirs(os.path.dirname(f_path), exist_ok=True)
                with open(f_path, "wb") as f:
                    f.write(req_body.encode("utf-8"))
                resp = "HTTP/1.1 201 Created\r\n\r\n"
            else:
                resp = get_resp("404 Not Found", "text/plain", "")
        elif crud == "GET":
            if path == "/":
                resp = get_resp("200 OK", "text/plain", "")
            elif path.startswith("/echo/"):
                string = path.split("/echo/")[1]
                resp = get_resp("200 OK", "text/plain", string)
            elif path == "/user-agent":
                ua = headers.get("User-Agent", "Unknown")
                resp = get_resp("200 OK", "text/plain", ua)
            elif path.startswith("/files/"):
                file = path.split("/files/")[1]
                f_path = os.path.join(base_directory, file)
                if os.path.exists(f_path):
                    with open(f_path, "rb") as f:
                        content = f.read()
                        resp = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {os.path.getsize(f_path)}\r\n\r\n{content.decode('utf-8')}"
                        f.close()
                else:
                    resp = get_resp("404 Not Found", "text/plain", "")
            else:
                resp = get_resp("404 Not Found", "text/plain", "")
        else:
            resp = get_resp("404 Not Found", "text/plain", "")

        socket.send(resp.encode())
    finally:
        socket.close()


def worker(connection, address):
    print(f"working on {address} ... for the robots ...")
    handle_req(connection)


# server application
def main():
    parser = argparse.ArgumentParser(description="file for robots.")
    parser.add_argument("--directory", type=str, help="directory")
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
