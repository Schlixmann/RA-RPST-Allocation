class Solution():
    def __init__(self, process):

        self.open_delete = False
        self.invalid_branches = False
        self.process = process
        self.ns = {"cpee1" : list(process.nsmap.values())[0]}

    def get_measure(self, measure, operator=sum):
        values = self.process.xpath(f".//cpee1:allocation/resource/resprofile/measures/{measure}", namespaces=self.ns)
        return operator([float(value.text) for value in values])

    def check_validity(self):
        tasks = self.process.xpath("//*[self::cpee1:call or self::cpee1:manipulate][not(ancestor::changepattern) and not(ancestor::cpee1:allocation)and not(ancestor::cpee1:children)]", namespaces=self.ns)
        for task in tasks:
            a = task.xpath("cpee1:allocation/*", namespaces=self.ns)
            if not task.xpath("cpee1:allocation/*", namespaces=self.ns):
                self.invalid_branches=True
                break
            else:
                self.invalid_branches=False
