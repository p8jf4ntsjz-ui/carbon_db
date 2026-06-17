import urllib.request, re
html = urllib.request.urlopen('https://nodejs.org/dist/').read().decode('utf-8')
versions = re.findall(r'href="(latest-v[0-9]+\.x/)"', html)
print(versions)
