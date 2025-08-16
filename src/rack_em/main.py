# rack_em is a python HTTP server created with a socket server
import argparse
import os
import socket
import threading


# request data is parsed
def find_data_in_req(data):
    info = data.split("\r\n")
    begin = info[0]
    func, loc, version = begin.split(" ")

    header_end = data.find("\r\n\r\n")
    body_start = header_end + 4

    if header_end != -1 and body_start != -1:
        req_body = data[body_start:-1] + data[-1]
    else:
        req_body = None

    headers = {}
    for line in info[1:]:
        if line == "":
            break
        h, v = line.split(": ", 1)
        if h == "Accept-Encoding":
            if v == "gzip":
                headers["Content-Encoding"] = v
            elif v == "invalid-encoding":
                continue
            else:
                headers[h] = v
        elif h == "User-Agent":
            headers[h] = v

    return func, loc, version, headers, req_body


# get the server response
def get_resp(state, type, body, headers):
    new_headers = [
        f"HTTP/1.1 {state}",
        f"Content-Type: {type}",
        f"Content-Length: {len(body) if body else 0}",
    ]
    for header in headers:
        new_headers.append(f"{header}: {headers[header]}")
    if body:
        new_headers.append("")
        new_headers.append(body)

    default = "\r\n".join(new_headers)
    return default + "\r\n\r\n"


# handler for the request
def handle_req(socket):
    try:
        http_req = socket.recv(1024).decode("utf-8")

        if not http_req:
            return

        crud, path, _, headers, req_body = find_data_in_req(http_req)

        if crud == "POST":
            if path.startswith("/files/"):
                file = path.split("/files/")[1]
                f_path = os.path.join(base_directory, file)
                os.makedirs(os.path.dirname(f_path), exist_ok=True)
                if req_body:
                    with open(f_path, "wb") as f:
                        f.write(req_body.encode("utf-8"))
                resp = "HTTP/1.1 201 Created\r\n\r\n"
            else:
                resp = get_resp("404 Not Found", "text/plain", "", headers)
        elif crud == "GET":
            if path == "/":
                resp = get_resp("200 OK", "text/plain", "", headers)
            elif path.startswith("/echo/"):
                string = path.split("/echo/")[1]
                resp = get_resp("200 OK", "text/plain", string, headers)
            elif path == "/user-agent":
                resp = get_resp("200 OK", "text/plain", headers["User-Agent"], headers)
            elif path.startswith("/files/"):
                file = path.split("/files/")[1]
                f_path = os.path.join(base_directory, file)
                if os.path.exists(f_path):
                    with open(f_path, "rb") as f:
                        content = f.read()
                        resp = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {os.path.getsize(f_path)}\r\n\r\n{content.decode('utf-8')}"
                        f.close()
                else:
                    resp = get_resp("404 Not Found", "text/plain", "", headers)
            else:
                resp = get_resp("404 Not Found", "text/plain", "", headers)
        else:
            resp = get_resp("404 Not Found", "text/plain", "", headers)

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
    print("server up up up ... port port port 4221 ...")

    try:
        while True:
            print("patiently waiting for that connection ...")
            conn, loc = server.accept()
            t = threading.Thread(target=worker, args=(conn, loc))
            t.start()
    except KeyboardInterrupt:
        print("\nserver going going going ...")
    finally:
        server.close()
        print("server down down down ...")


if __name__ == "__main__":
    main()
