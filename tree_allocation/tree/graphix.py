from lxml import etree
import uuid
from graphviz import Source
from tree_allocation.tree.R_RPST import *
# Sample XML data (replace this with your XML data)
#xml_data = open("xml_out.xml").read()

# Parse XML data
#root = etree.fromstring(xml_data)

# Initialize DOT content

class TreeGraph():
    def __init__(self):
        self.dot_content = 'digraph CallTree {\n'
        self.ns = {"cpee1" : "http://cpee.org/ns/description/1.0"}

    def add_node_to_dot(self, parent_id, element):
        return f'\t"{parent_id.attrib["unid"]}" -> "{element.attrib["unid"]}"\t ;\n'

    def add_visualization_res(self, element):
        
        self.dot_content += f'\t"{element.attrib["unid"]}" [label = "{element.attrib["id"]}: {element.attrib["name"]}"]\t; \n'

    def add_visualization_resprofile(self, element):
        
        self.dot_content += f'\t"{element.attrib["unid"]}" [label = "{element.attrib["id"]}: {element.attrib["role"]} \n {element.attrib["name"]}" shape=polygon sides=6]\t; \n'
            
    def add_visualization_task(self, element):
        name = get_label(etree.tostring(element))
        try:
            task_type = element.attrib["type"]
        except:
            task_type = "Core"
        try:
            direction = element.attrib["direction"]
        except:
            direction = "Core"

        self.dot_content += f'\t"{element.attrib["unid"]}" [label = "{element.attrib["id"]}: {name} \n Type: {task_type} \n Direction: {direction}" shape=rectangle]\t; \n'



    def tree_iter(self, node, branch=None): 

        if not branch:
            node.attrib["unid"] = str(uuid.uuid1())
            self.add_visualization_task(node)
            for child in node.xpath("cpee1:children/*", namespaces=self.ns):
                child.attrib["unid"] = str(uuid.uuid1())


        if node.tag == f"{{{self.ns['cpee1']}}}resource":
            if len(node.xpath("cpee1:resprofile/cpee1:children/*", namespaces=self.ns)) == 0:
                return
            
            for profile in node.xpath("cpee1:resprofile", namespaces=self.ns):
                profile.attrib["unid"] = str(uuid.uuid1())
                self.add_visualization_resprofile(profile)
                self.dot_content += self.add_node_to_dot(node, profile)
                for child in profile.xpath("cpee1:children/*", namespaces=self.ns):
                    child.attrib["unid"] = str(uuid.uuid1())
                    self.add_visualization_task(child)
                    self.dot_content += self.add_node_to_dot(profile, child)
                    self.tree_iter(child, True)


        if len(node.xpath("cpee1:children/*", namespaces=self.ns)) == 0:
            return
        if len(node.xpath("cpee1:children/*", namespaces=self.ns)) == 0 & (node.tag == f"{{{self.ns['cpee1']}}}resprofile"):
            self.add_visualization_resprofile(node)
            return

        if node.tag == f"{{{self.ns['cpee1']}}}call" or node.tag == f"{{{self.ns['cpee1']}}}call":
            for child in node.xpath("cpee1:children/*", namespaces=self.ns):
                child.attrib["unid"] = str(uuid.uuid1())
                self.add_visualization_res(child)
                self.dot_content += self.add_node_to_dot(node, child)
                self.tree_iter(child, True)

    def show(self, xml_str, format= 'png', filename='output_graph'):
        root = etree.fromstring(xml_str)
        self.tree_iter(root)
        self.dot_content += '}\n'
        print("Fin Dot:" , self.dot_content)
        # Write DOT content to a file (replace 'call_tree.dot' with your desired filename)
        with open('call_tree.dot', 'w') as dot_file:
            dot_file.write(self.dot_content)
        
        output_file = f"{filename}.{format}"
        
        source = Source(self.dot_content, filename='new_call_tree.dot', format='png')
        source.render(filename='new_call_tree', directory='.', cleanup=True, view=True)


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
