from src.tree.graphix import TreeGraph

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
    parser.add_argument("filename", help="An XML with a valid RA-PST")
    parser.add_argument("-o", "--OUTPUT", dest="outname",default="ra_pst_out", help="Set a specified path to save the resulting .png")
    parser.add_argument("-a", "--allocation", choices=["children", "allocation"], default="children", help= "Choose 'children' to print the full ra-pst, Choose 'allocation' to print the allocated RA-PST_instance")

    args = parser.parse_args()
    print("ARGS: ", args)

    show_graph(args.filename, output_path=args.outname, res_option=args.allocation)
