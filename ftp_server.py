from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# Create user: testuser / admin
authorizer = DummyAuthorizer()
authorizer.add_user("testuser", "admin", ".", perm="elradfmw")  # Full access

# Optional: allow anonymous login (for testing)
authorizer.add_anonymous(".", perm="elradfmw")

# Set up handler and server
handler = FTPHandler
handler.authorizer = authorizer

server = FTPServer(("127.0.0.1", 2121), handler)
print("🚀 FTP Server running at 127.0.0.1:21 with:")
print("   Username: testuser")
print("   Password: admin")
print("   Anonymous login: allowed")
server.serve_forever()
