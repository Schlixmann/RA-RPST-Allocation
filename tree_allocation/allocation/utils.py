from tree_allocation.tree.R_RPST import get_label
from lxml import etree
import random
import copy
import re
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

def vary_resource_changepatterns(proc_file, res_file, output_file=None, cp_ratio=0.8, in_de_re_ratios:list = [0.33, 0.33, 0.34], tasks=["dummy"], allowed_roles = ["level1", "level2", "level3"], cp_file = "tree_allocation/allocation/cp_descriptions.xml", insert_tasks = ["dummy"]):
    proc_file = "tests/test_processes/offer_process_paper.xml"
    with open(proc_file) as f:
        process = etree.fromstring(f.read())
        ns = {"cpee1" : list(process.nsmap.values())[0]}
        all_tasks = process.xpath("//cpee1:manipulate | //cpee1:call", namespaces=ns)

    with open(res_file) as f:
        res_tree = etree.fromstring(f.read())
    
    with open(cp_file) as f:
        cp_tree = etree.fromstring(f.read())

    res_profiles = res_tree.xpath("//resprofile")
    to_change = random.sample(res_profiles, k=round((len(res_profiles)-1 )* cp_ratio))

    changed_profiles = [] # split into 3 parts: insert, delete, replace
    used_r_ids = []
    directions = ["before", "after", "parallel"]

    test_strings = res_tree.xpath("//@id") + process.xpath("//@id")

    pattern = re.compile(r'rp|r_|a')
    try:
        curr_t_id = max([int(re.split("\\D", id)[-1]) for id in test_strings if not pattern.search(id)])
    except ValueError:
        curr_t_id = 0
    #curr_t_id = "r0"
    #pattern = re.compile(r'rp')
    #curr_rp_id = max([int(re.split("\D", id)[-1]) for id in test_strings if pattern.search(id)])
    
    for i in range(len(in_de_re_ratios)):
        changes = random.sample(to_change, k=round((len(to_change)-1) * in_de_re_ratios[i]))
        for profile in changes:
            roles = random.choices(allowed_roles, k=random.randint(1, len(allowed_roles)))
            curr_t_id =0
            match i:
                case 0: # insert
                    cp = copy.deepcopy(cp_tree.xpath("//changepattern[@type = 'insert']")[0])
                    task = all_tasks[random.randint(0, len(all_tasks)-1)]
                    label = insert_tasks[random.randint(0, len(insert_tasks)-1)]
                    cp.xpath("parameters/direction")[0].text = directions[random.randint(0, 2)]
                    cp.xpath("cpee1:description/cpee1:manipulate", namespaces=ns)[0].attrib['label'] = tasks[random.randint(0, len(tasks)-1)]
                    cp.xpath("cpee1:description/cpee1:manipulate", namespaces=ns)[0].attrib['id'] = "r" + str(curr_t_id)
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
                    cp.xpath("cpee1:description/cpee1:manipulate", namespaces=ns)[0].attrib['id'] = "r" + str(curr_t_id)
                    for role in roles:
                        element = etree.Element("resource")
                        element.text = role
                        cp.xpath(".//cpee1:resources", namespaces=ns)[0].append(element)
                    profile.append(cp)
                
                case 2: # replace
                    cp = copy.deepcopy(cp_tree.xpath("//changepattern[@type = 'replace']")[0])
                    task = all_tasks[random.randint(0, len(all_tasks)-1)]
                    label = insert_tasks[random.randint(0, len(insert_tasks)-1)]
                    cp.xpath("cpee1:description/cpee1:manipulate", namespaces=ns)[0].attrib['label'] = tasks[random.randint(0, len(tasks)-1)]
                    cp.xpath("cpee1:description/cpee1:manipulate", namespaces=ns)[0].attrib['id'] = "r" + str(curr_t_id)
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


def add_resources_for_inserts(res_file, tasks:list, allowed_roles, output_file=None, ratio= 0.2):
    with open(res_file) as f:
        res_tree = etree.fromstring(f.read())
    
    resources = res_tree.xpath("//resource")
    to_add = random.sample(resources, k=round((len(resources)-1 )* ratio))

    rp_ids = res_tree.xpath("//@id")
    pattern = re.compile(r'rp')
    curr_rp_id = max([int(re.split("\\D", id)[-1]) for id in rp_ids if pattern.search(id)])

    for resprofile in to_add:
        profile = copy.deepcopy(res_tree.xpath("//resprofile")[0])
        task = tasks[random.randint(0, len(tasks)-1)]
        role = allowed_roles[random.randint(0, len(allowed_roles)-1)]
        attribs = {"id": "rp_" + str(curr_rp_id), "name":task, "role":role, "task":task}
        for x in attribs.keys():
            profile.attrib[x] = str(attribs[x])
        resprofile.append(profile)
    
    if output_file:
        with open(output_file, "wb") as f:
            f.write(etree.tostring(res_tree))
    else:
        with open(res_file, "wb") as f:
            f.write(etree.tostring(res_tree))
    







    
    