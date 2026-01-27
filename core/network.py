import paramiko
import socks
import socket
import os


class GhostLink:
    def __init__(self):
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()

        known_hosts = os.path.expanduser("~/.ssh/known_hosts")
        if os.path.exists(known_hosts):
            try:
                self.client.load_host_keys(known_hosts)
            except Exception:
                pass
        self.sftp = None
        self.transport = None

    def connect(
        self,
        host,
        port,
        user,
        password=None,
        key_file=None,
        proxy_host=None,
        proxy_port=None,
    ):
        try:
            sock = None
            if proxy_host and proxy_port:
                sock = socks.socksocket()
                sock.set_proxy(socks.SOCKS5, proxy_host, int(proxy_port))
                sock.connect((host, int(port)))

            self.client.connect(
                hostname=host,
                port=port,
                username=user,
                password=password,
                key_filename=key_file,
                sock=sock,
                timeout=15,
                banner_timeout=15,
            )

            self.sftp = self.client.open_sftp()
            return True, "Secure Link Established" + (" (via Proxy)" if sock else "")
        except Exception as e:
            return False, f"Connection Failed: {str(e)}"

    def upload(self, local_path, remote_path):
        if not self.sftp:
            return False, "Not Connected"
        try:
            self.sftp.put(local_path, remote_path)
            return True, "Upload Complete"
        except Exception as e:
            return False, str(e)

    def close(self):
        if self.sftp:
            self.sftp.close()
        self.client.close()
