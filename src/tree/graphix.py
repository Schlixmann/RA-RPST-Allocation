from lxml import etree
import uuid
import os
from graphviz import Source
#from src.allocation.utils import get_label
#from src.tree.R_RPST import *

class TreeGraph():
    def __init__(self):
        self.dot_content = 'digraph CallTree {\n'
        self.ns = {"cpee1" : "http://cpee.org/ns/description/1.0"}



    def add_node_to_dot(self, parent_id, element):
        return f'\t"{parent_id.attrib["unid"]}" -> "{element.attrib["unid"]}"\t ;\n'

    def add_visualization_root(self, element):
        self.dot_content += f'\t"{element.attrib["unid"]}" [label = "{element.tag}"]\t; \n '

    def add_visualization_choose(self, element):
        self.dot_content += f'\t"{element.attrib["unid"]}" [label = "X" shape=diamond] \t; \n '

    def add_visualization_parallel(self, element):
        self.dot_content += f'\t"{element.attrib["unid"]}" [label = "+" shape=diamond]\t; \n '

    def add_visualization_res(self, element):
        self.dot_content += f'\t"{element.attrib["unid"]}" [label = "{element.attrib["id"]}: {element.attrib["name"]}"]\t; \n '

    def add_visualization_resprofile(self, element, measure="cost"):
        value = element.xpath(f"cpee1:measures/cpee1:{measure}", namespaces=self.ns) 
        if value:
            value = value[0].text
        self.dot_content += f'\t"{element.attrib["unid"]}" [label = "{element.attrib["id"]}: {element.attrib["role"]} \n {element.attrib["name"]} \n {measure} : {value}" shape=polygon sides=6]\t; \n'
            
    def add_visualization_task(self, element):
        name = self.get_label(etree.tostring(element))
        try:
            task_type = element.attrib["type"]
        except:
            task_type = "Core"
        try:
            direction = element.attrib["direction"]
        except:
            direction = "Core"

        self.dot_content += f'\t"{element.attrib["unid"]}" [label = "{element.attrib["id"]}: {name} \n Type: {task_type} \n Direction: {direction}" shape=rectangle]\t; \n'

    def tree_iter(self, node, res_option, branch=None ): 
        if node.tag in [f"{{{self.ns['cpee1']}}}alternative",f"{{{self.ns['cpee1']}}}otherwise", f"{{{self.ns['cpee1']}}}parallel_branch", f"{{{self.ns['cpee1']}}}choose", f"{{{self.ns['cpee1']}}}parallel"]:
            children = node.xpath("child::*[self::cpee1:manipulate or self::cpee1:call]", namespaces=self.ns)
        else:
            children = node.xpath(f"cpee1:{res_option}/*", namespaces=self.ns)


        if node.tag == f"{{{self.ns['cpee1']}}}description":
            
            if not branch:
                node.attrib["unid"] = str(uuid.uuid1())
                self.add_visualization_root(node)
                for child in node.xpath("child::*", namespaces=self.ns):
                    child.attrib["unid"] = str(uuid.uuid1())
                    if child.tag in [f"{{{self.ns['cpee1']}}}manipulate", f"{{{self.ns['cpee1']}}}call"]:
                        self.add_visualization_task(child)
                    elif child.tag == f"{{{self.ns['cpee1']}}}choose":
                        self.add_visualization_choose(child)
                    elif child.tag ==  f"{{{self.ns['cpee1']}}}parallel":
                        self.add_visualization_parallel(child)
                    
                    self.dot_content += self.add_node_to_dot(node, child)
                    self.tree_iter(child, res_option, True)

        elif node.tag == f"{{{self.ns['cpee1']}}}choose":
                for alternative in node.xpath("child::*", namespaces=self.ns):
                    alternative.attrib["unid"] = str(uuid.uuid1())
                    self.add_visualization_root(alternative)

                    self.dot_content += self.add_node_to_dot(node, alternative)
                    self.tree_iter(alternative,res_option, True)

        elif node.tag in [f"{{{self.ns['cpee1']}}}alternative", f"{{{self.ns['cpee1']}}}otherwise"]:
                for child in node.xpath("child::*[self::cpee1:manipulate or self::cpee1:call or self::cpee1:choose or self::cpee1:parallel]", namespaces=self.ns):
                    child.attrib["unid"] = str(uuid.uuid1())
                    if child.tag in [f"{{{self.ns['cpee1']}}}manipulate", f"{{{self.ns['cpee1']}}}call"]:
                        self.add_visualization_task(child)
                    elif child.tag == f"{{{self.ns['cpee1']}}}choose":
                        self.add_visualization_choose(child)
                    elif child.tag ==  f"{{{self.ns['cpee1']}}}parallel":
                        self.add_visualization_parallel(child)

                    self.dot_content += self.add_node_to_dot(node, child)
                    self.tree_iter(child, res_option,True)

        elif node.tag == f"{{{self.ns['cpee1']}}}parallel":
                for alternative in node.xpath("child::*", namespaces=self.ns):
                    alternative.attrib["unid"] = str(uuid.uuid1())
                    self.add_visualization_root(alternative)

                    self.dot_content += self.add_node_to_dot(node, alternative)
                    self.tree_iter(alternative,res_option, True)

        elif node.tag == f"{{{self.ns['cpee1']}}}parallel_branch":
                for child in node.xpath("child::*[self::cpee1:manipulate or self::cpee1:call or self::cpee1:choose or self::cpee1:parallel]", namespaces=self.ns):
                    child.attrib["unid"] = str(uuid.uuid1())
                    if child.tag in [f"{{{self.ns['cpee1']}}}manipulate", f"{{{self.ns['cpee1']}}}call"]:
                        self.add_visualization_task(child)
                    elif child.tag == f"{{{self.ns['cpee1']}}}choose":
                        self.add_visualization_choose(child)
                    elif child.tag ==  f"{{{self.ns['cpee1']}}}parallel":
                        self.add_visualization_parallel(child)

                    self.dot_content += self.add_node_to_dot(node, child)
                    self.tree_iter(child, res_option, True)

        elif node.tag == f"{{{self.ns['cpee1']}}}call" or node.tag == f"{{{self.ns['cpee1']}}}manipulate":
            if not branch:
                node.attrib["unid"] = str(uuid.uuid1())
                self.add_visualization_task(node)
                for child in node.xpath(f"cpee1:{res_option}/*", namespaces=self.ns):
                    child.attrib["unid"] = str(uuid.uuid1())
            
            if len(children) == 0:
                return node
            
            for child in children:
                child.attrib["unid"] = str(uuid.uuid1())
                self.add_visualization_res(child)
                self.dot_content += self.add_node_to_dot(node, child)
                self.tree_iter(child, res_option, True)
        
        elif node.tag == f"{{{self.ns['cpee1']}}}resprofile":
            if not branch:
                node.attrib["unid"] = str(uuid.uuid1())
                self.add_visualization_resprofile(node)
                for child in node.xpath("cpee1:children/*", namespaces=self.ns):
                    child.attrib["unid"] = str(uuid.uuid1())

            if len(children) == 0:
                return node
            
            for child in children:
                child.attrib["unid"] = str(uuid.uuid1())
                self.add_visualization_task(child)
                self.dot_content += self.add_node_to_dot(node, child)
                self.tree_iter(child, res_option, True)
            
        elif node.tag == f"{{{self.ns['cpee1']}}}resource":
            if not branch:
                node.attrib["unid"] = str(uuid.uuid1())
                self.add_visualization_res(node)
                for child in node.xpath("cpee1:resprofile", namespaces=self.ns):
                    child.attrib["unid"] = str(uuid.uuid1())

            if len(node.xpath("cpee1:resprofile", namespaces=self.ns)) == 0:
                return node
            
            for child in node.xpath("cpee1:resprofile", namespaces=self.ns):
                child.attrib["unid"] = str(uuid.uuid1())
                self.add_visualization_resprofile(child)
                self.dot_content += self.add_node_to_dot(node, child)
                self.tree_iter(child, res_option, True)

        else:
            raise("Unknown nodetype")
        
        return node
    

    def show(self, xml_str, format= 'png', filename='output_graph', directory='src/tree/graphs', view=True, res_option="children"):
        root = etree.fromstring(xml_str)

        self.tree_iter(root, res_option = res_option)
        self.dot_content += '}\n'
        
        # Write DOT content to a file (replace 'call_tree.dot' with your desired filename)
        folder_name = 'src/tree/tmp/'
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open('src/tree/tmp/call_tree.dot', 'w') as dot_file:
            dot_file.write(self.dot_content)
        
        output_file = f"{filename}.{format}"
        

        source = Source(self.dot_content, filename=f'{filename}.dot', format=format)
        source.render(filename=f'{filename}', directory=directory, cleanup=True, view=view)
    
    def get_label(self, element):
        el = type(element)
        elem_et = element if isinstance(element, etree._Element) else etree.fromstring(element)
        ns = {"cpee1" : list(elem_et.nsmap.values())[0]}
        if elem_et.tag == f"{{{ns['cpee1']}}}manipulate":
            return elem_et.attrib["label"]
        if elem_et.tag == f"{{{ns['cpee1']}}}call":
            to_ret = elem_et.xpath("cpee1:parameters/cpee1:label", namespaces=ns)[0].text
            return to_ret
        else:
            raise TypeError("Wrong Element Type: No Task element Given. Type is: ", elem_et.tag)

if __name__ == "__main__":

    with open("tests/test_output/times.xml", "rb") as f:
        #tree = etree.fromstring(f.read())
        TreeGraph().show(f.read(), filename=f"out_new") 


class ProcessTreeGraph():
    """
    Prints full ProcessTreegraph 
    -> Can I print the process Horizontal and the Allocations Vertical?
    -> Try!
    vgl:
    digraph G {
    rankdir=HR; // Sets the direction from top to bottom
    pad=0.5; // Adds space around the graph
    // Horizontal process nodes
    
    // Cluster for the "Process" subgraph with a box around it

    
    // Vertical tree for node a
    subgraph cluster_a {
        label="a";
        node [shape=circle, width=0.5, height=0.5,  color=lightgreen];
        a -> 1;
        a -> 2;
    }
    
    // Vertical tree for node b
    subgraph cluster_b {
        label="b";
        node [shape=circle, width=0.5, height=0.5, color=lightgreen];
        b -> 3 ->4;
        3 -> 5;
        b -> 6;
    }
    
    // Vertical tree for node c
    subgraph cluster_c {
        label="c";
        node [shape=circle, width=0.5, height=0.5,  color=lightgreen];
        c -> 7;
        c -> 8;
    }
    // Invisible edges to create separation between process and trees
    {rank= same; a; b; c; d;}
    a -> b -> c ;
    a -> d -> c ;
    

}

    """
# Write DOT content to a file (replace 'call_tree.dot' with your desired filename)
#with open('call_tree.dot', 'w') as dot_file:
#    dot_file.write(dot_content)

#print("DOT file generated successfully. Now use Graphviz to render the graph.")



# Read DOT content from the file
#with open('call_tree.dot', 'r') as dot_file:
#    dot_content = dot_file.read()

# Render the graph and save it as an image file
#source = Source(dot_content, filename='call_tree.dot', format='png')
#source.render(filename='call_tree', directory='.', cleanup=True, view=True)
