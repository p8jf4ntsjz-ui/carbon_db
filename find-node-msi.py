import urllib.request
import re
html = urllib.request.urlopen('https://nodejs.org/dist/latest-v20.x/').read().decode('utf-8')
files = re.findall(r'href="([^"]+x64\.msi)"', html)
print(files)