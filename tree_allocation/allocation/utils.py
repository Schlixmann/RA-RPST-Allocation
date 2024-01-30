from lxml import etree
import random
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
    
    