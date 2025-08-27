# Finding_base_suffixes_and_base_paths_in_suffix_trees
Suffix trees are fundamental data structure in stringology. We introduce two algorithms that index all strings/suffixes under all internal nodes in suffix tree in linear time and space. The first algorithms index all string under each internal node in suffix tree using the concept of base suffixes; while, the second algorithm index all paths between each internal node in suffix tree its descendant internal nodes. These indexes can contribute in resolving several strings problems such as DNA sequence analysis and approximate pattern matching problems. The full details of both algorithms/indexes are provided at https://www.biorxiv.org/content/10.1101/2021.10.25.465764v3. 


------------------------------------------------------------- Prerequisite ---------------------------------------------------------------
* Install bisect library from https://docs.python.org/3/library/bisect.html 

* Install the following library that will be used to build suffix trees:
https://github.com/ptrus/suffix-trees  

Then edit ./suffix_trees/STree.py as the followings:

- comment the following line, line 249, by inserting the character "#" at the beginning of the line. This will allow setting attributes to the suffix tree more freely.
```python
__slots__ = ['_suffix_link', 'transition_links', 'idx', 'depth', 'parent', 'generalized_idxs']
```

- In some procedures, we hashed internal nodes of suffix tree, to optimize this hashing we used only the combination of node index and node depth to identify uniquely an internal node instead of the original identification/naming of the nodes given by the library which is a bit long (shorter identification will use less space and speed up the lookup process for the hashed nodes). So replace the following two lines (which are line 264 and 265) 
```python
return ("SNode: idx:" + str(self.idx) + " depth:" + str(self.depth) +
                " transitons:" + str(list(self.transition_links.keys())))
```
with the line:
```python
return (str(self.idx) + "-" + str(self.depth))
```

------------------------------------------------------------- Preparation ----------------------------------------------------------------

Firstly, you need to convert the genome in fasta format to a one-line genome. This converting removes any non A, C, G, T, and N (case is sensitive) and headers from the FASTA file. This can be done using the script filter_DNA_file_to_4_bases_and_N.py by running the command:

```python
python3 convert_fasta_file_to_one_line_file $file.fasta > converted_fasta_file.oneline
```
----------------------------------------------------------- Running algorithms for finding base suffixes -----------------------------------------------------------

The input for the tools is the converted fasta file. These tools are applicable for Hamming distance and Wildcards matching. Edit distance to be implemented.  

Running command:
```python
python3 Finding_base_suffixes.py converted_fasta_file.oneline
```

A sample output:
```
Building Suffix Tree
Finished in 0.40969 seconds
------------------------------------------------------------------------------------------
Processing leaf and internal nodes
Number of leaf nodes is 47,961
Number of internal nodes is 31,627
Number of alphabets in the input data 15
Finished in 0.35694 seconds
------------------------------------------------------------------------------------------
Finding base suffixes using the linear algorithm
Number of OSHR leaf_nodes is 12,029
Number of OSHR internal nodes is 19,598
Total number of base suffixes 47,961
Total time cost: 226,179
Finished in 0.26442 seconds
------------------------------------------------------------------------------------------
Finding and checking base suffixes using the non-trivial algorithm 1 and O(n) space (hash-table)
=== All base suffixes at each internal nodes in ST are as expected ===
Total time cost: 517,853
Finished in 0.26787 seconds
------------------------------------------------------------------------------------------
Finding and checking base suffixes using the non-trivial algorithm 2 with additional log(Sigma) time factor
Sorting nodes link through suffix-links to each node in ST
Cost for sorting all List_of_nodes_suffix_linked_to_me 190,801
Finding base suffixes
=== All base suffixes at each internal nodes in ST are as expected ===
Total time cost: 1,000,879
Finished in 0.95413 seconds

```

----------------------------------------------------------- Running algorithms for finding base paths -----------------------------------------------------------

The input for the tools is the converted fasta file. These tools are applicable for Hamming distance and Wildcards matching. Edit distance to be implemented.  

Running command:
```python
python3 Finding_base_paths.py converted_fasta_file.oneline
```

A sample output:
```
Building Suffix Tree
Finished in 0.342 seconds
------------------------------------------------------------------------------------------
Processing leaf and internal nodes
Number of leaf nodes is 47,961
Number of internal nodes is 31,627
Number of alphabets in the input data 15
Finished in 0.35491 seconds
------------------------------------------------------------------------------------------
Finding base paths using the proposed algorithm
Indexing OSHR leaf nodes into a list from left to right
Number of OSHR leaf_nodes is 12,029
Number of OSHR internal nodes is 19,598
In total of 31,627
Cost for indexing OSHR leaf nodes into a list from left to right and sorting all List_of_nodes_suffix_linked_to_me: 190,801
Finding base paths
Number of OSHR leaf bottom base nodes for OSHR internal top base nodes 90,878
Number of OSHR internal bottom base nodes for OSHR internal top base nodes 2,387
Number of OSHR leaf bottom base nodes for OSHR leaf top base nodes 1,719
Number of OSHR internal bottom base nodes for OSHR leaf top base nodes 1,905

Total number of base paths 96,889
Total time cost: 356,618
Finished in 0.54863 seconds
------------------------------------------------------------------------------------------
Finding and checking base paths using the non-trivial algorithm
=== All base paths at each internal nodes in ST are as expected ===
Total time cost: 526,629
Finished in 1.58355 seconds

```

For contact, please email AA.12682@KHCC.JO (the email of the first author Anas Al-okaily).
