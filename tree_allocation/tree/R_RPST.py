from lxml import etree
import os

class CpeeElements():
    ns = dict()

    def __init__(self):
        self.elem_file = os.path.join(os.path.dirname(__file__), "process_descriptions/cpee_elements.xml")
        with open(self.elem_file) as f:
            self.elems_et = etree.fromstring(f.read())
        self.ns = {"cpee1" : list(self.elems_et.nsmap.values())[0]}
        ns = {"cpee1" : list(self.elems_et.nsmap.values())[0]}

        self.task_elements = [f"{{{ns['cpee1']}}}manipulate", f"{{{ns['cpee1']}}}call"]

    def parallel(self):
        return self.elems_et.xpath("cpee1:parallel", namespaces=self.ns)[0]
    
    def exclusive(self):
        return self.elems_et.xpath("cpee1:choose", namespaces=self.ns)[0]

    def call(self):
        return self.elems_et.xpath("cpee1:call", namespaces=self.ns)[0]
    
    def manipulate(self):
        return self.elems_et.xpath("cpee1:manipulate", namespaces=self.ns)[0]
    
def get_label(element):
    el = type(element)
    elem_et = etree.fromstring(element)
    ns = {"cpee1" : list(elem_et.nsmap.values())[0]}
    if elem_et.tag == f"{{{ns['cpee1']}}}manipulate":
        return elem_et.attrib["label"]
    if elem_et.tag == f"{{{ns['cpee1']}}}call":
        to_ret = elem_et.xpath("cpee1:parameters/cpee1:label", namespaces=ns)[0].text
        return to_ret
    else:
        raise TypeError("Wrong Element Type: No Task element Given. Type is: ", elem_et.tag) 


def get_allowed_roles(element):
    elem_et = etree.fromstring(element)
    ns = {"cpee1" : list(elem_et.nsmap.values())[0]}
    to_ret = [role.text for role in elem_et.xpath("cpee1:resources/cpee1:resource", namespaces=ns)]
    return to_ret
