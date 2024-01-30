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

def vary_resource_costs():
    pass