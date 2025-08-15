# rack_em is a python HTTP server created with a socket server
import argparse
import os
import pathlib
import re
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
def get_resp(state, type, body, file=False):
    if file:
        body_len = os.path.getsize(str(body))
        body_data = ""
    else:
        body_len = len(body)
        body_data = body

    headers = [
        f"HTTP/1.1 {state}",
        f"Content-Type: {type}",
        f"Content-Length: {body_len}",
        "",
        body_data,
    ]
    default = "\r\n".join(headers)
    return default


# get file from server
def get_resp_file(file):
    f = open(file, "rb")
    # filesize = os.path.getsize(file)
    body = f.read()
    f.close()
    # status = bytes("HTTP/1.1 200 OK\r\n", "utf-8")
    # headers = bytes(
    #     f"Content-Type: {type}/r/n",
    #     f"Content-Length: {str(filesize)}/r/n",
    # )
    default = body
    return default


# handler for the request
def handle_req(socket):
    try:
        data = socket.recv(1024).decode()
        if not data:
            return
        resp_file = None

        _, path, _, headers = find_data_in_req(data)
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
            if file in files:
                resp = get_resp("200 OK", "application/octet-stream", files[file], True)
                resp_file = get_resp_file(files[file])
            else:
                resp = get_resp("404 Not Found", "text/plain", "")
        else:
            resp = get_resp("404 Not Found", "text/plain", "")

        socket.send(resp.encode())
        if resp_file:
            socket.sendall(resp_file)
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

    global files
    files = {}
    pwd_files = [x for x in pathlib.Path(base_directory).glob("*.*")]
    for x in pwd_files:
        file_str = str(x)
        match = re.search(r"\w+.\w+$", file_str)
        if match:
            files[match.group()] = x

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
