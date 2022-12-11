# coding: utf8
"""
JSON Tree file parser for public release of FamilytreeDNA.com and yFull.com phylogenetic trees of haplogroups.
Expand as needed to process more about the tree.  Setup initially just for basic stats.

Copyright(c) Randy Harr, 2022.
License: GNU General Public License v3 or later
"""

import json
import requests
import re
import os

trees = {
    "ftdna_mtree": {
        "url": "https://www.familytreedna.com/public/mt-dna-haplotree/get",
        "file": "ftdna_mtree_extracted_2022-12-10.json" },
    "ftdna_ytree": {
        "url": "https://www.familytreedna.com/public/y-dna-haplotree/get",
        "file": "ftdna_ytree_extracted_2022-12-10.json" },
    "yfull_mtree": {
        "url": "https://github.com/YFullTeam/MTree/raw/master/mtree/current_mtree.json",
        "file": "yfull_mtree_1.02.13953_2022-01-01.json" },
    "yfull_ytree": {
        "url": "https://github.com/YFullTeam/YTree/raw/master/current_tree.json",
        "file": "yFull_ytree_10.07.0.json" }
}

cnts = {}

def get_json_tree(tree):

    r = requests.get(tree['url'], stream=True)
    with open(tree['file'], 'wb') as fd:
        for chunk in r.iter_content(chunk_size=1048576):
            fd.write(chunk)


def reset_cnts(tree):
    global cnts

    cnts = {
        'tree': tree,
        'date_ver': "",
        'tot_para': 0,
        'tot_empty_interior': 0,
        'tot_empty_leaf': 0,
        'tot_one_interior': 0,
        'tot_one_leaf': 0,              # Claimed issue
        'tot_multi_interior': 0,
        'tot_multi_leaf': 0,
        'tot_all_snps': 0,
        'avg_all_snps': 0,
        'tot_snp_aliases': 0,
        'tot_nodes_with_ids': 0,
        'tot_nodes': 0,
        'tot_nodes_with_no_kits': 0,
        'tot_kits': 0
    }


def calc_cnts(para, tot_snps, leaf, nodeid, kits, snp_aliases):
    """ Common calculation of values. Called per node in the tree with already extracted node values """
    if tot_snps == 0:  # Error? node without SNPs? (note: top level node exhibits this)
        if leaf:
            if para:
                cnts['tot_para'] += 1
            else:
                cnts['tot_empty_leaf'] += 1
        else:
            cnts['tot_empty_interior'] += 1
    elif tot_snps == 1:
        if leaf:
            cnts['tot_one_leaf'] += 1
        else:
            cnts['tot_one_interior'] += 1
    else:
        if leaf:
            cnts['tot_multi_leaf'] += 1
        else:
            cnts['tot_multi_interior'] += 1

    cnts['tot_all_snps'] += tot_snps
    cnts['tot_kits'] += kits
    cnts['tot_snp_aliases'] += snp_aliases

    if kits == 0:
        cnts['tot_nodes_with_no_kits'] += 1

    if nodeid:
        cnts['tot_nodes_with_ids'] += 1


def parse_ftdna_tree(tree, type):
    """ FTDNA tree is flat / linear, so single call with internal loop """
    global cnts

    cnts['date_ver'] = tree.get('publishedDate', "")    # mtree is not set now but may change
    ncnt = 0
    for nodeid, node in tree['allNodes'].items():
        nname = node["name"]
        ncnt += 1
        if not re.fullmatch("^[a-zA-Z0-9_.'!-]+$", nname):
            print(f'Odd charecters on {ncnt}th record: {nname}, length: {len(nname)}')

        para = False            # Have not found indicator for paragroup in their file

        children = node.get('children', {})
        leaf = len(children) == 0

        snps = node.get('variants', {})
        tot_snps = len(snps)
        neg_snps = 0
        if tot_snps == 1 and not snps[0]['variant']:    # They have records with one variant with blank name only
            tot_snps = 0
        else:
            for snp in snps:
                if snp['variant'][-1] == '!':
                    neg_snps += 1
        pos_snps = tot_snps - neg_snps

        snp_aliases = 0     # Have not found SNP aliases in their file

        # Seem to have kit count for node and all descendants; so only count up leaf node kitCounts.
        # Even then, many seem too high and not to be believed for mtree. But maybe not so for ytree?
        kits = node["kitsCount"] if leaf else 0
        if kits > 1000:
            print(f'Kits Count too high? {kits}, node {nodeid}')

        calc_cnts(para, tot_snps, leaf, node['name'], kits, snp_aliases)


def parse_yfull_tree(tree, type):
    """ Recursive call to walk the tree. Not flat. """
    global cnts

    para = tree['id'][-1] == '*' if len(tree['id']) > 0 else False      # Paragroup nodes have nothing except ID

    children = tree.get('children', [])
    leaf = len(children) == 0

    snpsstr = tree.get('snps', "")
    snps = () if not snpsstr else snpsstr.split(',')
    tot_snps = len(snps)
    neg_snps = snpsstr.count('!')
    snp_aliases = snpsstr.count('/')
    pos_snps = tot_snps - neg_snps

    kits = 0                                # Kits not defined in file

    calc_cnts(para, tot_snps, leaf, tree['id'], kits, snp_aliases)

    if not leaf:
        for child in children:
            parse_yfull_tree(child, type)


def process_ftdna_tree(tree_file, type):
    """ FTDNA Json files of their trees.  Data included but not processed includes Countries,
        occasional Surnames, and subBranchees (not children but sub-clade branch count it appears.
        Seems to be origin of the public tree and its data. mtree kitCounts seem to be incorrect
        and not like the subBranches either (cumulative of subBranches). mtree not date / version
        stamped in any way. Includes kit counts but no SNP aliases and paragroups. """
    global cnts

    reset_cnts(tree_file)

    with open(tree_file, "rb") as fd:
        parse_ftdna_tree(json.load(fd), type)

    all_nonzero_nodes = cnts['tot_one_leaf'] + cnts['tot_multi_leaf'] + \
                        cnts['tot_one_interior'] + cnts['tot_multi_interior']
    cnts['avg_all_snps'] = round(cnts['tot_all_snps'] / all_nonzero_nodes, 2)
    cnts['tot_nodes'] = all_nonzero_nodes + cnts['tot_para'] + cnts['tot_empty_leaf'] + cnts['tot_empty_interior']

    print(cnts)


def process_yfull_tree(tree_file, type):
    """ yFull Json files of their trees posted occassionaly to github.  Information skipped over is the 
        formed and TMRCA ages and ranges. Includes SNP aliases, paragroups but no kitCounts.  Content not 
        date / versions stamped but file name at the origin site can be (we link to "current" but site has
        the stamped file names. """
    global cnts

    reset_cnts(tree_file)

    with open(tree_file, "r") as fd:
        parse_yfull_tree(json.load(fd), type)

    all_nonzero_nodes = cnts['tot_one_leaf'] + cnts['tot_multi_leaf'] + \
                        cnts['tot_one_interior'] + cnts['tot_multi_interior']
    cnts['avg_all_snps'] = round(cnts['tot_all_snps'] / all_nonzero_nodes, 2)
    cnts['tot_nodes'] = all_nonzero_nodes + cnts['tot_para'] + cnts['tot_empty_leaf'] + cnts['tot_empty_interior']

    print(cnts)

# ***************MAIN PROGRAM*******************
if __name__ == '__main__':
    for key, tree in trees.items():
        if not os.path.isfile(tree['file']):
            get_json_tree(tree)
        type = "ytree" if "ytree" in key else "mtree" if "mtree" in key else "unk"
        if key.startswith("yfull"):
            process_yfull_tree(tree['file'], type)
        elif key.startswith("ftdna"):
            process_ftdna_tree(tree['file'], type)
    exit()