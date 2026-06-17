import urllib.request, re
url = 'https://nodejs.org/dist/latest-v26.x/'
html = urllib.request.urlopen(url).read().decode('utf-8')
files = re.findall(r'href="(node-v[0-9]+\.[0-9]+\.[0-9]+-x64\.msi)"', html)
print(files)
