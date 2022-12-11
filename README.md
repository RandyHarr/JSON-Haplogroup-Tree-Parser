# JSON-Haplogroup-Tree-Parser
A quickly created python utility to parse the phylogenetic tree of haplogroups from FTDNA and yFull

Simply run "python json_tree_parser.py", find the downloaded trees in the current directory and stats results printed to the terminal.

Here is an example run output at the time of creation (10 Dec 2022):

Kits Count too high? 2222, node 9596
{'tree': 'ftdna_mtree_extracted_2022-12-10.json', 'date_ver': '0001-01-01T00:00:00', 'tot_para': 0, 'tot_empty_interior': 10, 'tot_empty_leaf': 0, 'tot_one_interior': 1339, 'tot_one_leaf': 1389, 'tot_multi_interior': 1096, 'tot_multi_leaf': 1635, 'tot_all_snps': 13236, 'avg_all_snps': 2.42, 'tot_snp_aliases': 0, 'tot_nodes_with_ids': 5469, 'tot_nodes': 5469, 'tot_nodes_with_no_kits': 3099, 'tot_kits': 109652}
{'tree': 'ftdna_ytree_extracted_2022-12-10.json', 'date_ver': '2022-12-09T17:03:22.177', 'tot_para': 0, 'tot_empty_interior': 0, 'tot_empty_leaf': 0, 'tot_one_interior': 9647, 'tot_one_leaf': 6243, 'tot_multi_interior': 26393, 'tot_multi_leaf': 19684, 'tot_all_snps': 551370, 'avg_all_snps': 8.9, 'tot_snp_aliases': 0, 'tot_nodes_with_ids': 61967, 'tot_nodes': 61967, 'tot_nodes_with_no_kits': 38057, 'tot_kits': 52539}
{'tree': 'yfull_mtree_1.02.13953_2022-01-01.json', 'date_ver': '', 'tot_para': 7974, 'tot_empty_interior': 1, 'tot_empty_leaf': 6, 'tot_one_interior': 5986, 'tot_one_leaf': 9953, 'tot_multi_interior': 1989, 'tot_multi_leaf': 675, 'tot_all_snps': 26004, 'avg_all_snps': 1.4, 'tot_snp_aliases': 0, 'tot_nodes_with_ids': 26584, 'tot_nodes': 26584, 'tot_nodes_with_no_kits': 26584, 'tot_kits': 0}
{'tree': 'yFull_ytree_10.07.0.json', 'date_ver': '', 'tot_para': 16951, 'tot_empty_interior': 32, 'tot_empty_leaf': 27, 'tot_one_interior': 4192, 'tot_one_leaf': 2704, 'tot_multi_interior': 12739, 'tot_multi_leaf': 9054, 'tot_all_snps': 298963, 'avg_all_snps': 10.42, 'tot_snp_aliases': 58197, 'tot_nodes_with_ids': 45698, 'tot_nodes': 45699, 'tot_nodes_with_no_kits': 45699, 'tot_kits': 0}

Modify as desired to extract more or walk the tree as desired.  A similar mechanism is likely used by Cladefinder from Hunter Provyn. Maybe you can modify his code to use the FTDNA tree in addition to the yFull tree it now processes? That is an eventual hope and to then incorporate into WGS Extract to replace / add-to Haplogroup and yLeaf there. (Note clear if the mito cladefinder can be modified that way though.)
