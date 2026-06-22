import urllib.request
import os
import subprocess
import tempfile
url = 'https://nodejs.org/dist/latest-v20.x/node-v20.20.2-x64.msi'
dest = os.path.join(tempfile.gettempdir(), 'node-v20.20.2-x64.msi')
urllib.request.urlretrieve(url, dest)
subprocess.run(['msiexec', '/i', dest, '/qn', '/norestart'], check=True)
os.remove(dest)
print('Node installer completed')
