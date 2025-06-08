def recv_line(conn):
    data = b""
    while not data.endswith(b"\n"):
        data += conn.recv(1)
    return data.decode().strip()