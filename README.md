# JSON-Haplogroup-Tree-Parser
A quickly created python utility to parse the phylogenetic tree of haplogroups from FTDNA and yFull

Simply run "python json_tree_parser.py", find the downloaded trees in the current directory and stats results printed to the terminal.

Here is an example run output at the time of creation (10 Dec 2022):
```
Kits Count too high? 2223, node 9596
{'tree': 'ftdna_mtree_extracted_2022-12-10.json', 'date_ver': '0001-01-01T00:00:00', 'tot_para': 0, 'tot_empty_interior': 10, 'tot_empty_leaf': 0, 'tot_one_interior': 1339, 'tot_one_leaf': 1389, 'tot_multi_interior': 1096, 'tot_multi_leaf': 1635, 'tot_all_snps': 13236, 'avg_all_snps': 2.42, 'tot_snp_aliases': 0, 'tot_nodes_with_ids': 5469, 'tot_nodes': 5469, 'tot_nodes_with_no_kits': 3097, 'tot_kits': 109801}
{'tree': 'ftdna_ytree_extracted_2022-12-10.json', 'date_ver': '2022-12-15T16:35:18.7', 'tot_para': 0, 'tot_empty_interior': 0, 'tot_empty_leaf': 0, 'tot_one_interior': 9673, 'tot_one_leaf': 6267, 'tot_multi_interior': 26500, 'tot_multi_leaf': 19744, 'tot_all_snps': 552946, 'avg_all_snps': 8.89, 'tot_snp_aliases': 0, 'tot_nodes_with_ids': 62184, 'tot_nodes': 62184, 'tot_nodes_with_no_kits': 38190, 'tot_kits': 52772}
{'tree': 'yfull_mtree_1.02.18515_2022-12-16.json', 'date_ver': '', 'tot_para': 9988, 'tot_empty_interior': 0, 'tot_empty_leaf': 7, 'tot_one_interior': 7851, 'tot_one_leaf': 12515, 'tot_multi_interior': 2139, 'tot_multi_leaf': 452, 'tot_all_snps': 30119, 'avg_all_snps': 1.31, 'tot_snp_aliases': 0, 'tot_nodes_with_ids': 32952, 'tot_nodes': 32952, 'tot_nodes_with_no_kits': 32952, 'tot_kits': 0}
{'tree': 'yFull_ytree_10.07.0.json', 'date_ver': '', 'tot_para': 16951, 'tot_empty_interior': 32, 'tot_empty_leaf': 27, 'tot_one_interior': 4192, 'tot_one_leaf': 2704, 'tot_multi_interior': 12739, 'tot_multi_leaf': 9054, 'tot_all_snps': 298963, 'avg_all_snps': 10.42, 'tot_snp_aliases': 58197, 'tot_nodes_with_ids': 45698, 'tot_nodes': 45699, 'tot_nodes_with_no_kits': 45699, 'tot_kits': 0}
```

Modify as desired to extract more or walk the tree as desired.  A similar mechanism is likely used by Cladefinder from Hunter Provyn. Maybe you can modify his code to use the FTDNA tree in addition to the yFull tree it now processes? That is an eventual hope and to then incorporate into WGS Extract to replace / add-to Haplogroup and yLeaf there. (Note clear if the mito cladefinder can be modified that way though.)
