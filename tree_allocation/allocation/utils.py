from tree_allocation.tree.R_RPST import get_label
from lxml import etree
import random
import copy
# iterate open tasks
def get_next_task(tasks_iter, solution=None):
    if solution:
        ns = {"cpee1" : list(solution.process.nsmap.values())[0]}
    while True:
        task = next(tasks_iter, "end")
        if task == "end":
            #print("Final Task reached. solution found")
            if solution:
                solution.check_validity()
            return task
        
        # check that next task was not deleted:
        elif solution: 
            if not solution.process.xpath(f"//*[@id='{task.attrib['id']}'][not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=ns):
                pass
            else:
                break
        else:
            break
    return task

def vary_resource_costs(file_path, measure, max_val=100):
    with open(file_path) as f:
        res_tree = etree.fromstring(f.read())

    elms = res_tree.xpath(f"//{measure}")
    for elm in elms:
        elm.text = str(random.randint(1, max_val))

    with open(file_path, "wb") as f:
        f.write(etree.tostring(res_tree))

def vary_resource_changepatterns(proc_file, res_file, output_file, cp_ratio=0.8, in_de_re_ratios:list = [0.33, 0.33, 0.34], allowed_roles = ["level1", "level2", "level3"], cp_file = "tree_allocation/allocation/cp_descriptions.xml", insert_tasks = ["dummy"]):
    proc_file = "tests/test_processes/offer_process_paper.xml"
    with open(proc_file) as f:
        res_tree = etree.fromstring(f.read())
        ns = {"cpee1" : list(res_tree.nsmap.values())[0]}
        all_tasks = res_tree.xpath("//cpee1:manipulate | //cpee1:call", namespaces=ns)

    with open(res_file) as f:
        res_tree = etree.fromstring(f.read())
    
    with open(cp_file) as f:
        cp_tree = etree.fromstring(f.read())

    res_profiles = res_tree.xpath("//resprofile")
    to_change = random.sample(res_profiles, k=round((len(res_profiles)-1 )* cp_ratio))

    changed_profiles = [] # split into 3 parts: insert, delete, replace
    directions = ["before", "after", "parallel"]
    
    for i in range(len(in_de_re_ratios)):
        changes = random.sample(to_change, k=round((len(to_change)-1) * in_de_re_ratios[i]))
        for profile in changes:
            roles = random.choices(allowed_roles, k=random.randint(1, len(allowed_roles)))
            match i:
                case 0: # insert
                    cp = copy.deepcopy(cp_tree.xpath("//changepattern[@type = 'insert']")[0])
                    task = all_tasks[random.randint(0, len(all_tasks)-1)]
                    label = insert_tasks[random.randint(0, len(insert_tasks)-1)]
                    cp.xpath("parameters/direction")[0].text = directions[random.randint(0, 2)]
                    cp.xpath("cpee1:description/cpee1:manipulate", namespaces=ns)[0].attrib['label'] = "dummy"
                    for role in roles:
                        element = etree.Element("resource")
                        element.text = role
                        cp.xpath(".//cpee1:resources", namespaces=ns)[0].append(element)
                    profile.append(cp)
                
                case 1: # delete
                    cp = copy.deepcopy(cp_tree.xpath("//changepattern[@type = 'delete']")[0])
                    task = all_tasks[random.randint(0, len(all_tasks)-1)]
                    label = get_label(etree.tostring(task))
                    cp.xpath("cpee1:description/cpee1:manipulate", namespaces=ns)[0].attrib['label'] = label
                    for role in roles:
                        element = etree.Element("resource")
                        element.text = role
                        cp.xpath(".//cpee1:resources", namespaces=ns)[0].append(element)
                    profile.append(cp)
                
                case 2: # replace
                    cp = copy.deepcopy(cp_tree.xpath("//changepattern[@type = 'replace']")[0])
                    task = all_tasks[random.randint(0, len(all_tasks)-1)]
                    label = insert_tasks[random.randint(0, len(insert_tasks)-1)]
                    cp.xpath("cpee1:description/cpee1:manipulate", namespaces=ns)[0].attrib['label'] = "dummy"
                    for role in roles:
                        element = etree.Element("resource")
                        element.text = role
                        cp.xpath(".//cpee1:resources", namespaces=ns)[0].append(element)
                    profile.append(cp)
    
    if output_file:
        with open(output_file, "wb") as f:
            f.write(etree.tostring(res_tree))
    else:
        with open(res_file, "wb") as f:
            f.write(etree.tostring(res_tree))
    
    print("done")



    
    