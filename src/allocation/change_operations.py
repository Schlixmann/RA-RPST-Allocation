from ..tree.node import *
from lxml import etree
from ..helpers import *
import logging
logger = logging.getLogger(__name__)

    
    
def create_change_operation(allocated_branch: Node, process_model: str):
    print("Operations of allocated_branch: ", allocated_branch.get_all_nodes(key="task"))
    # define namespaces
    ns = {"cpee2": "http://cpee.org/ns/properties/2.0", "cpee1":"http://cpee.org/ns/description/1.0"}
    resources = allocated_branch.get_all_nodes(key="resource")
    process_model = etree.fromstring(process_model)
    
 
    rp = (next(rp for rp in resources[0].resource_obj.resource_profiles if rp == resources[0].resource_profile))
    #TODO maybe for multiple change patterns

    print(f"All nodes: {[task.get_name for task in allocated_branch.get_all_nodes(key='task')]}")
    for x in allocated_branch.get_all_nodes(key="task"):
        # find element to manipulate:
        task_id = x.id

        with open("output/process2.xml", "wb") as f:
            f.write(etree.tostring(process_model))
        #try:
        print(task_id)
        elem_to_manipulate = process_model.xpath(f".//cpee1:*[@id='{task_id}']", namespaces=ns)[0]
        print(elem_to_manipulate)
        #except:
        #    elem_to_manipulate = process_model.xpath(f".//*[@id='{task_id}']", namespaces=ns)[0]    

        for child in x.children:
            allocation_attrib = elem_to_manipulate.find(f".//cpee1:resources", ns).attrib["allocated_to"] 
            if allocation_attrib != "not_allocated":
                allocation_attrib = allocation_attrib + " & " + str(child.get_name) + " rp:" + str(child.resource_profile.name)
                elem_to_manipulate.find(f".//cpee1:resources", ns).attrib["allocated_to"] = allocation_attrib
            else:
                elem_to_manipulate.find(f".//cpee1:resources", ns).attrib["allocated_to"]  = str(child.get_name) + " rp:" + str(child.resource_profile.name)
            if len(child.resource_profile.change_patterns) > 0:
                for pattern in child.resource_profile.change_patterns:
                    open("output/pattern.xml", "wb").write(etree.tostring(pattern))
                    a = pattern.attrib["type"]
                    match a:
                        case "replace":
                            to_insert = pattern.findall(f".//cpee1:description/", ns)
                            
                            for change in to_insert[::-1]:
                                
                                process_model.find(f".//cpee1:*[@id='{task_id}']", ns).addnext(change)
                            elem_to_manipulate.getparent().remove(elem_to_manipulate)


                        case "insert":

                            print("create insertion: ", task_id)
                            to_insert = pattern.xpath(f"cpee1:description/*", namespaces=ns)
                            logger.debug(f"to_insert: {to_insert}")
                            for change in to_insert[::-1]:
                                logger.debug(f"{task_id}")
                                logger.debug(process_model.xpath(f".//cpee1:*[@id='{task_id}']", namespaces=ns))
                                insert_index = process_model.xpath("//cpee1:*", namespaces=ns).index(process_model.xpath(f".//cpee1:*[@id='{task_id}']", namespaces=ns)[0])
                                logger.debug(f"inser_index: {insert_index}")
                                logger.debug(f"Match pattern: {[elem for elem in pattern.xpath('//changepattern/parameters/direction' , namespaces=ns)]}")
                                
                                print("Insertion direction: ", pattern.xpath("./parameters/direction")[0].text)
                                
                                match pattern.xpath("./parameters/direction")[0].text:
                                    case "before":
                                        print("Inserting before")
                                        process_model.xpath(f".//cpee1:*[@id='{task_id}']", namespaces=ns)[0].addprevious(change)
                                        logger.debug("Added to process model!")
                                    case "after":
                                        print("Inserting after")
                                        process_model.xpath(f".//cpee1:*[@id='{task_id}']", namespaces=ns)[0].addnext(change)
                                    case "parallel":
                                        print("Inserting parallel")
                                        print("insert_index: ", insert_index)
                                        to_remove = process_model.xpath(f".//cpee1:*[@id='{task_id}']", namespaces=ns)[0]
                                        print("to_remove: ", to_remove)
                                        process_model.xpath(f".//cpee1:*[@id='{task_id}']", namespaces=ns)[0].addnext(etree.fromstring("<parallel wait=\"-1\" cancel=\"last\"></parallel>"))
                                                                               
                                        
                                        etree.SubElement(process_model.xpath(f".//cpee1:*[@id='{task_id}']", namespaces=ns)[0].getnext(), "parallel_branch", {"pass": "", "local":""})
                                        
                                        
                                        with open("output/process3.xml", "wb") as f:
                                            f.write(etree.tostring(process_model))
                                        
                                        process_model.xpath(f".//cpee1:*[@id='{task_id}']", namespaces=ns)[0].getnext().xpath("./*")[-1].append(change)
                                        etree.SubElement(process_model.xpath(f".//cpee1:*[@id='{task_id}']", namespaces=ns)[0].getnext(), "parallel_branch", {"pass": "", "local":""})
                                        process_model.xpath(f".//cpee1:*[@id='{task_id}']", namespaces=ns)[0].getnext().xpath("./*")[-1].append(to_remove)
                                        

                    with open("output/process1.xml", "wb") as f:
                        f.write(etree.tostring(process_model))

            else:
                pass
                # BaseCase to allocate an element
                # allocate element:
                #allocation_attrib = elem_to_manipulate.find(f".//cpee1:resources", ns).attrib["allocated_to"] 
                #if allocation_attrib != "not_allocated":
                #    allocation_attrib = allocation_attrib + " & " + str(child.get_name) + " rp:" + str(child.resource_profile.name)
                #    elem_to_manipulate.find(f".//cpee1:resources", ns).attrib["allocated_to"] = allocation_attrib
                #else:
                #    elem_to_manipulate.find(f".//cpee1:resources", ns).attrib["allocated_to"]  = str(child.get_name) + " rp:" + str(child.resource_profile.name)



                
    return etree.tostring(process_model), process_model
    


#TODO show that task is allocated and which resource
# test with insert and conditions
# realize rest api 
# test with different settings! 

if __name__ == "__main__":
    pass
