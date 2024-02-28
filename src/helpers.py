from src.proc_resource import *
from pptree import *
from lxml import etree
import requests
import logging
logger = logging.getLogger(__name__)

def get_all_resources(resource_url, file_path:str):
        print("File_path: ", file_path)
        print("Res request url ", resource_url)
        payload = {'resource_file': file_path}
        r = requests.get(url = resource_url, params=payload)
        print("Resource status_code: ", r.status_code)
        root = etree.fromstring(r.content)
        reslist = []
        init_measure_dict = dict(map(lambda e: (e.tag, 0), root.xpath("//measures/*")))
        print(f"Dict of Measures: ", init_measure_dict)
        
        for element in root.xpath("//resource"):
            print(f"Create resource with id {element.attrib['id']}")
            res = Resource(element.attrib["name"])
            
            for profile in element.xpath("resprofile"):
                change_patterns = [] + profile.xpath("changepattern")
                measure_dict = init_measure_dict | dict(map(lambda e: (e.tag, float(e.text)), profile.xpath("measures/*")))
                
                logger.debug(f"init_measure_dict of {element} : {profile}: {measure_dict}")
                logger.debug(f"check_init_measure: {init_measure_dict}")
                
                res.create_resource_profile(profile.attrib["name"], profile.attrib["role"], task=profile.attrib["task"], change_patterns=change_patterns, measure=measure_dict)

            reslist.append(res)
            
        return reslist


def get_all_tasks(cpee_url):
        # define namespaces
        ns = {"cpee2": "http://cpee.org/ns/properties/2.0", 
            "cpee1":"http://cpee.org/ns/description/1.0"}
        
        # send get request and save response
        r = requests.get(url = cpee_url)

        # parse xml:
        root = etree.fromstring(r.content)
        tasks = root.xpath(".//cpee1:call | .//cpee1:manipulate", namespaces=ns)
        
        return tasks

def get_process_model(cpee_url):
        # send get request and save response
        r = requests.get(url = cpee_url)

        # parse xml:
        root = etree.fromstring(r.content)
        xml_string = r.content
        #with open("./config/xml_model.xml", "wb") as f:
        #    f.write(xml_string)
        return xml_string, root
