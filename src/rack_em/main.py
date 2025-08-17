# rack_em is a python HTTP socket server

import argparse
import gzip
import os
import socket
import threading

SERVER = "localhost"
PORT = 4221


# request data is parsed
def parse_request(data):
    request_array = data.split("\r\n")
    request_status_line = request_array[0]
    method, addr, version = request_status_line.split(" ")

    request_header_end = data.find("\r\n\r\n")
    request_body_start = request_header_end + 4

    request_body = None
    if request_header_end != -1 and request_body_start != -1:
        request_body = data[request_body_start:-1] + data[-1]

    headers = {}
    for header in request_array[1:]:
        if header == "":
            break
        header_key, header_value = header.split(": ", 1)
        if header_key == "Accept-Encoding":
            accept_encodings = header_value.split(",")
            for e in accept_encodings:
                encoding = e.replace(" ", "")
                if encoding == "gzip":
                    headers[f"Content-Encoding-{encoding}"] = encoding
                else:
                    headers[f"Content-Encoding-{encoding}"] = None
            else:
                headers[header_key] = header_value
        elif header_key == "User-Agent":
            headers[header_key] = header_value
        elif header_key == "Connection" and header_value == "close":
            headers[header_key] = header_value

    return method, addr, version, headers, request_body


# get the server response
def get_response(state, type, body, headers, request_count):
    response_headers = []
    response_headers.append(f"HTTP/1.1 {state}")
    response_headers.append(f"Content-Type: {type}")
    for key in headers:
        if key.startswith("Content-Encoding"):
            if headers[key] is not None:
                response_headers.append(f"Content-Encoding: {headers[key]}")
                if isinstance(body, str):
                    data = body.encode("utf-8")
                else:
                    data = body
                compressed_data = gzip.compress(data, compresslevel=6)
                body = compressed_data
            else:
                continue
        elif key == "Accept-Encoding":
            continue
        elif key == "Connection":
            if request_count == 2:
                response_headers.append(f"{key}: {headers[key]}")
            else:
                continue
        else:
            response_headers.append(f"{key}: {headers[key]}")

    if body:
        response_headers.append(f"Content-Length: {len(body)}\r\n")
        response_headers.append(body)
    elif isinstance(body, str):
        response_headers.append("\r\n")

    default = b""
    for head in response_headers:
        if isinstance(head, bytes):
            return default + head
        else:
            rep = head + "\r\n"
            default = default + rep.encode()
    return default[:-2]


# handler for the request
def handle_request(socket):
    request_count = 0

    with socket as s:
        while True:
            request = s.recv(1024).decode("utf-8")
            request_count += 1

            if not request:
                break

            method, request_url, _, request_headers, request_body = parse_request(
                request
            )

            if method == "POST":
                if request_url.startswith("/files/"):
                    file = request_url.split("/files/")[1]
                    f_path = os.path.join(base_dir, file)
                    os.makedirs(os.path.dirname(f_path), exist_ok=True)
                    if request_body:
                        with open(f_path, "wb") as f:
                            f.write(request_body.encode("utf-8"))
                    response = "HTTP/1.1 201 Created\r\n\r\n"
                else:
                    response = get_response(
                        "404 Not Found",
                        "text/plain",
                        "",
                        request_headers,
                        request_count,
                    )
            elif method == "GET":
                if request_url == "/":
                    response = get_response(
                        "200 OK", "text/plain", "", request_headers, request_count
                    )
                elif request_url.startswith("/echo/"):
                    string = request_url.split("/echo/")[1]
                    response = get_response(
                        "200 OK", "text/plain", string, request_headers, request_count
                    )
                elif request_url == "/user-agent":
                    response = get_response(
                        "200 OK",
                        "text/plain",
                        request_headers["User-Agent"],
                        request_headers,
                        request_count,
                    )
                elif request_url.startswith("/files/"):
                    file = request_url.split("/files/")[1]
                    f_path = os.path.join(base_dir, file)
                    if os.path.exists(f_path):
                        with open(f_path, "rb") as f:
                            content = f.read()
                            response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {os.path.getsize(f_path)}\r\n\r\n{content.decode('utf-8')}"
                            f.close()
                    else:
                        response = get_response(
                            "404 Not Found",
                            "text/plain",
                            "",
                            request_headers,
                            request_count,
                        )
                else:
                    response = get_response(
                        "404 Not Found",
                        "text/plain",
                        "",
                        request_headers,
                        request_count,
                    )
            else:
                response = get_response(
                    "404 Not Found", "text/plain", "", request_headers, request_count
                )

            if isinstance(response, str):
                s.send(response.encode())
            else:
                s.sendall(response)

            if "Connection" in request_headers.keys() and request_count == 2:
                if request_headers["Connection"] == "close":
                    s.shutdown()


def request_worker(connection, address):
    print(f"working {address} for the robots ...\n")
    handle_request(connection)


# server application
def main():
    parser = argparse.ArgumentParser(description="a python http server for robots")
    parser.add_argument("--dir", type=str, help="directory for server files")
    args = parser.parse_args()

    global base_dir
    base_dir = args.directory

    with socket.create_server((SERVER, PORT), reuse_port=True) as s:
        s.listen(5)
        print(f"serving up {SERVER} @ port {PORT} ...\n")

        try:
            while True:
                print("waiting for connection ...\n")
                conn, addr = s.accept()
                t = threading.Thread(target=request_worker, args=(conn, addr))
                t.start()
        except KeyboardInterrupt:
            print("\nserver going going going ...\n")
        finally:
            s.close()
            print("server down down down ...\n")


if __name__ == "__main__":
    main()
