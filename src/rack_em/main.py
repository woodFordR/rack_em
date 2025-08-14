import socket


# request is parsed
def seeker(data):
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


def getter(state, type, body):
    headers = [
        f"HTTP/1.1 {state}",
        f"Content-Type: {type}",
        f"Content-Length: {len(body)}",
        "",
        body,
    ]
    default = "\r\n".join(headers)
    return default


def handler(socket):
    try:
        data = socket.recv(1024).decode()
        if not data:
            return

        _, path, _, headers = seeker(data)
        if path == "/":
            receive = getter("200 OK", "text/plain", "")
        elif path.startswith("/echo/"):
            string = path.split("/echo")[1]
            receive = getter("200 OK", "text/plain", string)
        elif path == "/user-agent":
            ua = headers.get("User-Agent", "Unknown")
            receive = getter("200 OK", "text/plain", ua)
        else:
            receive = getter("404 Not Found", "text/plain", "")

        socket.send(receive.encode())
    finally:
        socket.close()


def main():
    server = socket.create_server(("localhost", 4221), reuse_port=True)
    print("SERVER UP, PORT 4221")

    try:
        while True:
            print("Patiently Waiting For Connection!")
            connected, location = server.accept()
            print(f"{location} connected as a robot...")

            handler(connected)
            connected.close()
    except KeyboardInterrupt:
        print("\nServer going going going ...")
    finally:
        server.close()
        print("Server down down down ...")


if __name__ == "__main__":
    main()
