from proc_resource import *
import time 
from lxml import etree


def get_all_resources(path_to_xml):
        with open(str(path_to_xml)) as f:
            root = etree.fromstring(f.read())
        
        for element in root.findall("resource"):
            print(f"Create resource with id {element.attrib['id']}")
            res = Resource(element.attrib["name"])
            for profile in element.findall("resprofile"):
                change_patterns=[]
                for cp in profile.findall("changepattern"):
                    change_patterns.append(cp)
                res.create_resource_profile(profile.attrib["name"], profile.attrib["role"], task=profile.attrib["task"], change_pattern=change_patterns)

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
        tasks = []
        for task in root.xpath(".//cpee1:call | .//cpee1:manipulate", namespaces=ns):
            tasks.append(task)
        
        return tasks

def print_allo_tree(node):
    if len(node.children) == 0:
          print(node)
    else:
        print(node)
        for child in node.children:
            print_allo_tree(child)

if __name__ == "__main__":
    reslist = []

    import requests

    cpee_url =  f"https://cpee.org/flow/engine/16646/properties/description/"
    frag_url = f"https://cpee.org/flow/engine/15344/properties/description/"

    ns = {"cpee2": "http://cpee.org/ns/properties/2.0", 
            "cpee1":"http://cpee.org/ns/description/1.0"}
    
    resources = get_all_resources("./config/res_config.xml")
    tasklabels = []
    for task in get_all_tasks(cpee_url):
        try:
            tasklabels.append(task.attrib["label"])
            
        except:
            try:
                attrib = task.find(".//cpee1:parameters", ns)
                if not attrib.find(".//cpee1:label", ns).text:
                     raise Exception("Task {} has no label.".format(task.attrib["id"]))
                else:
                     tasklabels.append(attrib.find(".//cpee1:label", ns).text )
            except Exception as e:
                print(e)
                continue
    print(tasklabels)
    print(resources)
    from tree_allocation.allocation.allocation import *
    allocation_tree = get_allocation(tasklabels[0], resources)
    print_allo_tree(allocation_tree)

## TODO: allocation algorithm (tree)

    