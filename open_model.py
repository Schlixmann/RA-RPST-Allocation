from lxml import etree
import requests
import json
import os
import sys

with open("processes/plain_instance.xml") as f: 
    process = etree.fromstring(f.read())
    ns = {"cpee2" : list(process.nsmap.values())[0]}

xml = open(os.getcwd() +"/" + str(sys.argv[1])).read() 

data = process.xpath("cpee2:description", namespaces=ns)[0]
data.remove(data.xpath("*")[0])
data.append(etree.fromstring(xml))
data = etree.tostring(process)

response = requests.post(
    url = "https://cpee.org/flow/start/",

    headers= {
      'Content-Type': 'text/xml',
      'Content-ID': 'xml'
    },
    data = data
  )

print(response)
  
os.system(f"xdg-open https://cpee.org/flow/edit.html?monitor={json.loads(response.content)['CPEE-INSTANCE-URL']}")

