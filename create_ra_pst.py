from src.tree.graphix import TreeGraph
from src.allocation.solution_search import Genetic,Brute, combine_pickles
from src.allocation.cpee_allocation import *

from lxml import etree
import requests
import json
import os
import sys
import argparse


def show_graph(filename, output_path=f"ra_pst_out", res_option="children"):
    with open(filename, "r") as f:
        TreeGraph().show(f.read(), filename=output_path, directory="", res_option=res_option)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="""Get a graphviz representation of a RA-PST. You can print both the full RA-PST or a fully allocated Solution. \n
                                        To force the calculation of all solutions: use -b (be aware of long execution times) \n
                                        You can access the results by running 'results_presentation/results.ipynb' """)
    parser.add_argument("process_file", help="An XML with a valid RA-PST")
    parser.add_argument("resource_file")
    parser.add_argument("-o", "--OUTPUT", dest="outname",default="ra_pst.xml", help="Set a specified path to save the resulting RA-PST")
    parser.add_argument("-p", "--print_ra_pst", action="store_true", help="Create RA-PST graphviz representation and save it as RA-PST.png" )

    args = parser.parse_args()
    print("ARGS: ", args)

    with open(args.process_file) as f: 
        process_xml = f.read()

    tree = etree.fromstring(process_xml)
    if list(tree.nsmap.values())[0] == 'http://cpee.org/ns/properties/2.0':
        proc_ns = {'cpee1':'http://cpee.org/ns/description/1.0'}
        process_xml = etree.tostring(tree.xpath(f"//cpee1:description", namespaces = proc_ns)[0])
        print("Created Model from testset")

    with open(args.resource_file) as f:
        resource_xml = etree.fromstring(f.read())

    #print(process_xml)
    
    process_allocation = ProcessAllocation(process_xml, resource_xml)
    process_allocation.allocate_process()  

    with open(args.outname, "wb") as f:
        f.write(process_allocation.ra_rpst)

    if args.print_ra_pst:
        show_graph(args.outname)
    
