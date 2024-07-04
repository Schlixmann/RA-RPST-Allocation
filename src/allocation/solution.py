from lxml import etree


class Solution():
    def __init__(self, process):

        self.open_delete = False
        self.invalid_branches = False
        self.process = process
        self.ns = {"cpee1" : list(process.nsmap.values())[0], "allo": "http://cpee.org/ns/allocation"}

    def get_measure(self, measure, operator=sum, flag=False):
        """Returns 0 if Flag is set wrong or no values are given, does not check if allocation is valid"""
        if flag:
            values = self.process.xpath(f".//allo:allocation/cpee1:resource/cpee1:resprofile/cpee1:measures/cpee1:{measure}", namespaces=self.ns)
        else:
            values = self.process.xpath(f".//allo:allocation/resource/resprofile/measures/{measure}", namespaces=self.ns)
        return operator([float(value.text) for value in values])

    def check_validity(self):
        #TODO Expand to also check if same resource is allocated in a parallel branch
        self.process = etree.fromstring(etree.tostring(self.process))
        tasks = self.process.xpath("//*[self::cpee1:call or self::cpee1:manipulate][not(ancestor::cpee1:changepattern) and not(ancestor::cpee1:allocation)and not(ancestor::cpee1:children)]", namespaces=self.ns)

        for task in tasks:
            a = task.xpath("cpee1:allocation/*", namespaces=self.ns)
            with open("text.xml", "wb") as f:
                f.write(etree.tostring(task))
            if not task.xpath("cpee1:allocation/*", namespaces=self.ns):
                self.invalid_branches=True
                break
            #else:
            #    self.invalid_branches=False

