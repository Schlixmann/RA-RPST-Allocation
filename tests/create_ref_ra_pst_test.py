from src.allocation.cpee_allocation import TaskAllocation, ProcessAllocation

from lxml import etree
import unittest



class TestCreateRA_PST(unittest.TestCase):
        
    def test_create_ra_pst(self):
        RESOURCE_FILES = {"resource_config/offer_resources_heterogen.xml" : "heterogen",
        "resource_config/offer_resources_close_maxima.xml" : "close_maxima",
        "resource_config/offer_resources_many_invalid_branches.xml" : "invalid_branches",
        "resource_config/offer_resources_heterogen_no_deletes.xml" : "no_deletes",
        "resource_config/offer_resources_plain_fully_synthetic_small.xml" : "fully_synthetic",
        }
        PROCESS_FILE = "processes/offer_process_paper.xml"

        for path, name in RESOURCE_FILES.items():
            with open(PROCESS_FILE) as f: 
                    task_xml = f.read()
            with open(path) as f:
                resource_et = etree.fromstring(f.read())
                
            process_allocation = ProcessAllocation(task_xml, resource_url=resource_et)
            process_allocation.allocate_process() 

            with open(f"tests/reference_ra_psts/{name}", "wb") as f:
                f.write(process_allocation.ra_rpst)