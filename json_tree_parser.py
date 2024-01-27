# coding: utf8
"""
JSON Tree file parser for public release of FamilytreeDNA.com and yFull.com phylogenetic trees of haplogroups.
Expand as needed to process more about the tree.  Setup initially just for basic stats.

v1.1 Updated to use current date to create output file name. Refactored some code to generalize parsing better.
     Added example json from vendors to guide parser updates.

todo: Search ybrowse DB for SNP aliases to add to FTDNA tree (missing)

todo: yFull tree is hierarchical json. FTDNA is flat json.
      Develop a common form so tools can use either tree interchangeably.
      
todo: maybe add a generator for tree walking. Definitely a search for a specific haplogroup based on a given SNP.
      And maybe, given a haplogroup / SNP, return the path of haplogroups from the root to that node.
      check cladefinder (python2 though) and yleaf 3 for ideas. Add support for FTDNA to yleaf?

todo: FTDNA only dates the yTree; not mTree.  But FTDNA's date is at the very end of the file.
      yFull trees are in github which you could possibly get a date and version from.
      Try to only update when newer available, not based on if extracted today or not.

Copyright(c) Randy Harr, 2022-2024.
License: GNU General Public License v3 or later
"""

import json
import requests
import re
import os
from datetime import datetime


trees = {
    "ftdna_mtree": { "url": "https://www.familytreedna.com/public/mt-dna-haplotree/get" },
    "ftdna_ytree": { "url": "https://www.familytreedna.com/public/y-dna-haplotree/get" },
    "yfull_mtree": { "url": "https://github.com/YFullTeam/MTree/raw/master/mtree/current_mtree.json" },
    "yfull_ytree": { "url": "https://github.com/YFullTeam/YTree/raw/master/current_tree.json" }
}

# ++++++++++++++++++++++++++ Start of example code for tree stats summary ++++++++++++++++++++++++++
cnts = {}

def reset_cnts(tree_name):
    global cnts

    cnts = {
        'tree': tree_name,
        'date_ver': "",                 # Only FTDNA y Tree is date stamped (unfortunately)
        'tot_paragrps': 0,
        'tot_nosnps_interior': 0,
        'tot_nosnps_leaf': 0,
        'tot_onesnp_interior': 0,
        'tot_onesnp_leaf': 0,              # Claimed issue
        'tot_multisnps_interior': 0,
        'tot_multisnps_leaf': 0,
        'tot_all_snps': 0,
        'avg_all_snps': 0,
        'tot_snp_aliases': 0,
        'tot_nodes_with_ids': 0,
        'tot_nodes': 0,
        'tot_nodes_with_no_kits': 0,
        'tot_kits': 0
    }


def calc_pernode_cnts(para, tot_snps, leaf, nodeid, kits, snp_aliases):
    """  Common (among vendor) calculation of tree summary values. Called per node in the tree with common
         extracted values.  Fills global dictionary cnts.  """
    global cnts

    # Leaf here means no subclades, interior means subclades; tot_empty/_one/_multi refers to number of SNPs in the node
    if tot_snps == 0:  # Error? node without SNPs? (note: top level node appears this way)
        if leaf:
            if para:
                cnts['tot_paragrps'] += 1
            else:
                cnts['tot_nosnps_leaf'] += 1
        else:
            cnts['tot_nosnps_interior'] += 1
    elif tot_snps == 1:
        if leaf:
            cnts['tot_onesnp_leaf'] += 1
        else:
            cnts['tot_onesnp_interior'] += 1
    else:   # tot_snps > 1
        if leaf:
            cnts['tot_multisnps_leaf'] += 1
        else:
            cnts['tot_multisnps_interior'] += 1

    cnts['tot_all_snps'] += tot_snps
    cnts['tot_kits'] += kits
    cnts['tot_snp_aliases'] += snp_aliases

    if kits == 0:
        cnts['tot_nodes_with_no_kits'] += 1

    if nodeid:
        cnts['tot_nodes_with_ids'] += 1


def calc_tree_summary_cnts():
    """  Calculate final summary cnts[] values based on values collected while parsing tree per node.  """
    global cnts

    all_nonzero_nodes = cnts['tot_onesnp_leaf'] + cnts['tot_multisnps_leaf'] + \
                        cnts['tot_onesnp_interior'] + cnts['tot_multisnps_interior']
    cnts['avg_all_snps'] = round(cnts['tot_all_snps'] / all_nonzero_nodes, 2)
    cnts['tot_nodes'] = all_nonzero_nodes + cnts['tot_paragrps'] + cnts['tot_nosnps_leaf'] + cnts['tot_nosnps_interior']


#++++++++++++++++++++++++++ Start of Example Tree Parser (to support summary stats) ++++++++++++++++++++++++++

def get_jsonfile(outfile, url):
    """  Rad JSON file from URL and store into local file. Could keep in memory but want to save for user. """

    r = requests.get(url, stream=True)

    with open(outfile, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=1048576):        # Need to limit how much is read each grab
            fd.write(chunk)
            

def parse_ftdna_tree(jtree):
    """ FTDNA tree is flat / linear, so single call with loop through each entry.
        User can rewrite the parser for what they need.
        This one simply summarizes the whole tree into the cnts[] dictionary entries.

        Appears to be the origin of the public tree and its data.
        Data not processed here includes Countries, occasional Surnames, and subBranches. subBranches appears to
        be the cumulative branch count below this Clade (sum of sub-clade subBranches count). mTree kitCounts appears
        to be cumulative also; but not in ytree. ytree is date / version stamped. No SNP aliases and paragroups.

        {
          "allNodes":{                                 # Linear list of haplogroups / nodes / blocks
            "4350":{
              "haplogroupId":4350,
              "parentId":0,
              "name":"RSRS",
              "isRoot":true,                           # How they designate root
              "root":"L",                              # Single letter "root"
              "artificialRoot":"L",                    # Only in yTree
              "kitsCount":0,
              "subBranches":5468,
              "bigYCount":0,
              "countryCounts":[ {"countryCode":"X", "name":"Unknown Origin", kitsCounts:4}, ... ],
              "variants":[ {"variant":"","snpId":0} ], # One entry but false
              "children":[4351,4508],                  # Entry only in non-leafs
              "isBackbone":false,                      # Only in yTree
              "isSNPAssuranceGroup":false },           # Only in yTree
            "4351":{
              "haplogroupId":4351,
              "parentId":4350,                         # Not in Roots entries below
              "name":"L0",                             # In yTree, name always starts with major letter then SNP variant
              "isRoot":false,
              "root":"L",                              # major letter root as they show in their tree
              "artificialRoot":"L",                    # Only in yTree
              "kitsCount":9,                           # Kits terminated at this node?
              "subBranches":156,
              "bigYCount":0,
              "countryCounts":[                        # Not in all haplogroups / nodes
                {"countryCode":"ENG","name":"England","kitsCounts":112},    # kitsCounts may be cumultive like sub
                {"countryCode":"SE","name":"Sweden","kitsCounts":111}, ...],
              "variants":[                             # Note: no aliases (always at least one entry)
                  {"variant":"G263A","position":263,"ancestral":"G","derived":"A","region":"HVR2","snpId":0},
                  {"variant":"C1048T","position":1048,"ancestral":"C","derived":"T","region":"CR","snpId":0}, ... ],
              "children": [4354, 4395],                # Sub-clades; no paragroups it appears
              "isBackbone":false,                      # Only in yTree
              "isSNPAssuranceGroup":false  },          # Only in yTree
            "4354": ... },
          "roots":[ {"haplogroupID":6574,...},... ],   # Haplogroup entry copy except "isRoot" set true; python list
          "allCountries":[ "Afghanistan","Åland","Albania"  ....],      # Duplicative with entries in Haplogroups?
          "id":0,                                      # Only yTree has an actual version ID
          "publishedDate":"0001-01-01T00:00:00"        # Only yTree has an actual date
        }
    """
    global cnts

    cnts['date_ver'] = jtree.get('publishedDate', "")    # mtree is not set now but may change
    ncnt = 0
    for nodeid, node in jtree['allNodes'].items():
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
                if snp['variant'][-1] == '!':       # Variants matching reference are "negative" (trailing !)
                    neg_snps += 1
        pos_snps = tot_snps - neg_snps

        snp_aliases = 0     # Have not found SNP aliases in their file

        # Seem to have kit count for node and all descendants; so only count up leaf node kitCounts.
        # Even then, many seem too high and not to be believed for mtree. But maybe not so for ytree?
        kits = node["kitsCount"] if leaf else 0
        if kits > 1000:
            print(f'Kits Count too high? {kits}, node {nodeid}')

        calc_pernode_cnts(para, tot_snps, leaf, node['name'], kits, snp_aliases)


def parse_yfull_tree(jtree):
    """ Strutured tree so recursive call to walk the tree.
        User can rewrite the parser for what they need.
        This one simply summarizes the whole tree into the cnts[] dictionary entries.

        yFull Json files of their trees posted occassionaly to github.  Information skipped over is the
        formed and TMRCA ages and ranges. Includes SNP aliases, paragroups but no kitCounts.  Content not
        date / versions stamped but file name at the origin site can be (we link to "current" but site has
        the stamped file names.

        # yFull uses array [] instead of named objects {}. So is a Python list instead of a dictionary with keys.
        # You have to walk the structure which mimics the tree.  Not flat list of haplogroups like FTDNA.
        { "formed": "-",
          "tmrca": 235900,
          "snps": "",
          "tmrcalowage": 228300,
          "tmrcahighage": 243700,
          "formedlowage": "-",
          "formedhighage": "-",
          "id": "",
          "children": [
            { "formed": 235900,
              "tmrca": 37600,
              "snps": "FGC25750/YP2704/V2222, A2655/YP2714/V2299, ....",     # comma separated string with aliases
              "tmrcalowage": 33100,
              "tmrcahighage": 42200,
              "formedlowage": 228300,
              "formedhighage": 243700,
              "id": "A00",
              "children": [
                { "formed": 37600,
                  "tmrca": 37600,
                  "snps": "",
                  "tmrcalowage": 33100,
                  "tmrcahighage": 42200,
                  "formedlowage": 33100,
                  "formedhighage": 42200,
                  "id": "A00*" },       # paragroup so no children (should be same with leaf haplogroups as well)
                { "formed": 37600,
                  "tmrca": 1500,
                  "snps": "A2692, FGC25522/YP2561, ... ",
                  "tmrcalowage": 1050,
                  "tmrcahighage": 2000,
                  "formedlowage": 33100,
                  "formedhighage": 42200,
                  "id": "A00-Y125399",
                  "children": [
                  { "formed": .....
    """
    global cnts

    para = jtree['id'][-1] == '*' if len(jtree['id']) > 0 else False      # Paragroup nodes have nothing except ID

    children = jtree.get('children', [])
    leaf = len(children) == 0

    snpsstr = jtree.get('snps', "")
    snps = () if not snpsstr else snpsstr.split(',')    # Haplogroup SNPs / variants are in a comma-separated string
    tot_snps = len(snps)
    neg_snps = snpsstr.count('!')
    snp_aliases = snpsstr.count('/')        # yFull includes aliases as well as variants
    pos_snps = tot_snps - neg_snps

    kits = 0                                # Kits not defined in file

    calc_pernode_cnts(para, tot_snps, leaf, jtree['id'], kits, snp_aliases)

    if not leaf:
        for child in children:
            parse_yfull_tree(child)


# ++++++++++++++++++++++++++ MAIN EXAMPLE PROGRAM ++++++++++++++++++++++++++
if __name__ == '__main__':

    # For each of the trees we have a URL for ... retrieve and parse to collect and print summary stats
    for key, tree in trees.items():

        treetype = "ytree" if key.endswith("ytree") else \
                   "mtree" if key.endswith("mtree") else \
                    None
        vendor, fform = ("yfull", "r") if key.startswith("yfull") else \
                        ("ftdna", "rb") if key.startswith("ftdna") else \
                        (None, None)

        # Name the output file by the vendor, treetype and current date
        today = datetime.today().strftime('%Y-%m-%d')
        jsonfile = f'{key}_extracted_{today}.json'

        # Files are not date / version stamped. So get a json file of a tree if not yet done today
        if not os.path.isfile(jsonfile):
            get_jsonfile(jsonfile, tree['url'])

        # Load the json tree file into memory as a (hierarchical) dictionary
        with open(jsonfile, fform) as jfd:
            jasontree = json.load(jfd)

        # Just for demonstration here.  Summarize the tree contents.
        # User can write their own parser to do what they want.
        reset_cnts(jsonfile)

        if vendor == "yfull":
            parse_yfull_tree(jasontree)
        elif vendor == "ftdna":
            parse_ftdna_tree(jasontree)

        calc_tree_summary_cnts()
        
        print(cnts)     # Print tree summary metrics

