from lxml import etree
import uuid
from graphviz import Source
from tree_allocation.tree.R_RPST import *

class TreeGraph():
    def __init__(self):
        self.dot_content = 'digraph CallTree {\n'
        self.ns = {"cpee1" : "http://cpee.org/ns/description/1.0"}

    def add_node_to_dot(self, parent_id, element):
        return f'\t"{parent_id.attrib["unid"]}" -> "{element.attrib["unid"]}"\t ;\n'

    def add_visualization_res(self, element):
        self.dot_content += f'\t"{element.attrib["unid"]}" [label = "{element.attrib["id"]}: {element.attrib["name"]}"]\t; \n'

    def add_visualization_resprofile(self, element, measure="cost"):
        value = element.xpath(f"cpee1:measures/cpee1:{measure}", namespaces=self.ns) 
        if value:
            value = value[0].text
        self.dot_content += f'\t"{element.attrib["unid"]}" [label = "{element.attrib["id"]}: {element.attrib["role"]} \n {element.attrib["name"]} \n {measure} : {value}" shape=polygon sides=6]\t; \n'
            
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
        children = node.xpath("cpee1:children/*", namespaces=self.ns)
        if node.tag == f"{{{self.ns['cpee1']}}}call" or node.tag == f"{{{self.ns['cpee1']}}}manipulate":
            if not branch:
                node.attrib["unid"] = str(uuid.uuid1())
                self.add_visualization_task(node)
                for child in node.xpath("cpee1:children/*", namespaces=self.ns):
                    child.attrib["unid"] = str(uuid.uuid1())
            
            if len(children) == 0:
                return node
            
            for child in children:
                child.attrib["unid"] = str(uuid.uuid1())
                self.add_visualization_res(child)
                self.dot_content += self.add_node_to_dot(node, child)
                self.tree_iter(child, True)
        
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
                self.tree_iter(child, True)
            
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
                self.tree_iter(child, True)

        else:
            raise("Unknown nodetype")
        
        return node

    def show(self, xml_str, format= 'png', filename='output_graph', directory='tree_allocation/tree/graphs', view=True):
        root = etree.fromstring(xml_str)
        self.tree_iter(root)
        self.dot_content += '}\n'
        
        # Write DOT content to a file (replace 'call_tree.dot' with your desired filename)
        with open('tree_allocation/tree/tmp/call_tree.dot', 'w') as dot_file:
            dot_file.write(self.dot_content)
        
        output_file = f"{filename}.{format}"
        
        source = Source(self.dot_content, filename=f'{filename}.dot', format=format)
        source.render(filename=f'{filename}', directory=directory, cleanup=True, view=view)


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
