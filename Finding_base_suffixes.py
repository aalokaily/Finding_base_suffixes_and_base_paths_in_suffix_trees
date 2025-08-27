from suffix_trees import STree 
from collections import defaultdict
import time
import math
import sys
import bisect


 
print ("Building Suffix Tree")

def Build_suffix_tree():
    global tree
    
    input_file = sys.argv[1]    
    text = ""
    with open(input_file) as file_in:        
        for line in file_in:
            if line[0] != ">":
                text += line.strip()
                
    
    tree = STree.STree(text)
    
    
    
start = time.time()   
Build_suffix_tree()
print ("Finished in", round((time.time() - start), 5), "seconds")
print ("------------------------------------------------------------------------------------------")


def get_leaf_nodes(tree, node):
    results = []
    nodes_stack = [(node, False)]  # (node, visited_flag)

    while nodes_stack:
        current_node, visited = nodes_stack.pop()

        if not visited:
            # Push the node again, marked as visited (after children)
            nodes_stack.append((current_node, True))

            # Push children in reverse sorted order to process left → right

            for child_node in current_node.transition_links.values():
                nodes_stack.append((child_node, False))
        else:
            # After children: collect leaf nodes
            if current_node.is_leaf():
                results.append(current_node)

    return results
    
    
print ("Processing leaf and internal nodes")
 
def process_leaf_and_internal_nodes(tree):    
    
    setattr(tree, "number_leaf_nodes", 0)
    setattr(tree, "number_internal_nodes", 0)
    setattr(tree, "M", [-1] * len(tree.word)) 
     
    
    nodes_stack = [(tree.root, False)]
    
    while nodes_stack:
        current_node, visited = nodes_stack.pop()
        
        if not visited:
            # push back current node with visited=True (postorder processing)
            nodes_stack.append((current_node, True))
            
            # push children (to be processed first, since postorder)
            for child_node in current_node.transition_links.values():
                nodes_stack.append((child_node, False))
                                      
        else:
            # alongside processing
            if current_node.is_leaf():
                # Assigning leaf nodes unique keys
                current_node.index_of_leaf_in_ST = tree.number_leaf_nodes                     
                tree.number_leaf_nodes += 1
                
                # creating auxiliary lists 
                tree.M[current_node.idx] = current_node
                
                if not hasattr(current_node.parent, "index_of_leftmost_leaf_in_ST"):
                    setattr(current_node.parent, "index_of_leftmost_leaf_in_ST", current_node.index_of_leaf_in_ST)
                elif current_node.index_of_leaf_in_ST < current_node.parent.index_of_leftmost_leaf_in_ST:
                    current_node.parent.index_of_leftmost_leaf_in_ST = current_node.index_of_leaf_in_ST
                if not hasattr(current_node.parent, "index_of_rightmost_leaf_in_ST"):
                    setattr(current_node.parent, "index_of_rightmost_leaf_in_ST", current_node.index_of_leaf_in_ST)
                elif current_node.index_of_leaf_in_ST > current_node.parent.index_of_rightmost_leaf_in_ST:
                    current_node.parent.index_of_rightmost_leaf_in_ST = current_node.index_of_leaf_in_ST
                    
            else:
                tree.number_internal_nodes += 1
                setattr(current_node, "List_of_base_suffixes", [])  
                # construct implicit OSHR tree
                if current_node._suffix_link is not None and current_node != tree.root:
                    temp = current_node._suffix_link
                    if not hasattr(temp, "List_of_nodes_suffix_linked_to_me"):
                        setattr(temp, "List_of_nodes_suffix_linked_to_me", [])
                    temp.List_of_nodes_suffix_linked_to_me.append(current_node)
            
                if not hasattr(current_node.parent, "index_of_leftmost_leaf_in_ST"):
                    setattr(current_node.parent, "index_of_leftmost_leaf_in_ST", current_node.index_of_leftmost_leaf_in_ST)
                elif current_node.index_of_leftmost_leaf_in_ST < current_node.parent.index_of_leftmost_leaf_in_ST:
                    current_node.parent.index_of_leftmost_leaf_in_ST = current_node.index_of_leftmost_leaf_in_ST
                if not hasattr(current_node.parent, "index_of_rightmost_leaf_in_ST"):
                    setattr(current_node.parent, "index_of_rightmost_leaf_in_ST", current_node.index_of_rightmost_leaf_in_ST)
                elif current_node.index_of_rightmost_leaf_in_ST > current_node.parent.index_of_rightmost_leaf_in_ST:
                    current_node.parent.index_of_rightmost_leaf_in_ST = current_node.index_of_rightmost_leaf_in_ST
            
                
            
            
    print ("Number of leaf nodes is", "{:,}".format(tree.number_leaf_nodes))
    print ("Number of internal nodes is", "{:,}".format(tree.number_internal_nodes))
    print ("Number of alphabets in the input data", len(tree.root.transition_links) - 1)



start = time.time()
process_leaf_and_internal_nodes(tree)
print ("Finished in", round((time.time() - start), 5), "seconds")
print ("------------------------------------------------------------------------------------------")
    
  
print ("Finding base suffixes using the linear algorithm")

def Find_base_suffixes_using_linear_algorithm(tree):
    # Note that reference leaf nodes and reference internal nodes will not be created explicitly as they will not be used by any process. However, in case a user 
    # may need them, the algorithm that create them explicitly is provided as supplemntary at the bottom of this script with name Find_base_suffixes_using_linear_algorithm2
    
    cost = 0
    OSHR_leaf_nodes_key_counter = 0
    OSHR_internal_nodes_key_counter = 0
    base_suffix_counter = 0
    
    nodes_stack = [(tree.root, False)]
    
    while nodes_stack:
        cost += 1
        current_node, visited = nodes_stack.pop()
        
        if not visited:
            # push back current node with visited=True (postorder processing)
            nodes_stack.append((current_node, True))
            
            # push children (to be processed first, since postorder)
            for child_node in current_node.transition_links.values():
                nodes_stack.append((child_node, False))                                          
        else:
            # alongside processing
            if current_node.is_leaf():
                if current_node.idx + 1 < tree.number_leaf_nodes:
                    # this code computes base suffixes derived from reference leaf nodes. 
                    leaf_node_of_next_suffix_index = tree.M[current_node.idx + 1]                                    
                    if leaf_node_of_next_suffix_index.parent != current_node.parent._suffix_link:
                        temp = leaf_node_of_next_suffix_index.parent
                        end_node = current_node.parent._suffix_link
                        while True:
                            cost += 1
                            if temp == end_node:
                                if current_node.parent == tree.root: # if so, then we must add this suffix as a base suffix to end_node unlike other cases (end_node must be tree.root)
                                    temp.List_of_base_suffixes.append(leaf_node_of_next_suffix_index.idx + temp.depth) 
                                    base_suffix_counter += 1 
                                break
                            else:
                                temp.List_of_base_suffixes.append(leaf_node_of_next_suffix_index.idx + temp.depth)
                                temp = temp.parent
                                base_suffix_counter += 1
                            
            else:
                # this code computes base suffixes derived from reference internal nodes.
                if current_node._suffix_link.parent != current_node.parent._suffix_link:
                    top_node = current_node.parent._suffix_link 
                    bottom_node = current_node._suffix_link

                    temp = bottom_node.parent
                    while temp != top_node:
                        cost += 1
                        for leaf_node in get_leaf_nodes(tree, current_node):
                            suffix_index_of_leaf_node = leaf_node.idx
                            temp.List_of_base_suffixes.append(suffix_index_of_leaf_node + 1 + temp.depth)
                            base_suffix_counter += 1
                        temp = temp.parent
                        
                
                if hasattr(current_node, "List_of_nodes_suffix_linked_to_me"):
                    OSHR_internal_nodes_key_counter += 1
                else:
                    OSHR_leaf_nodes_key_counter += 1       
                

    # compute the case for suffix 0 as there is no previous index for index 0 
    cost += 1
    temp = tree.M[0]                                     
    while temp != tree.root:
        temp = temp.parent
        temp.List_of_base_suffixes.append(0 + temp.depth)
        base_suffix_counter += 1
        cost += 1
        
        
    # this a special cases and for the root only. The suffix-link of child internal node of a root usually link to the root. In case not, 
    # then the node that the child internal node link to must be bottom-node for the root node.
    cost += 1
    current_node = tree.root
    for node in current_node.transition_links.values():
        cost += 1
        if node.is_leaf():
            if node.idx + 1 < tree.number_leaf_nodes:
                leaf_node_of_next_suffix_index = tree.M[node.idx + 1]
                if leaf_node_of_next_suffix_index.parent == tree.root:
                    current_node.List_of_base_suffixes.append(leaf_node_of_next_suffix_index.idx)
                    base_suffix_counter += 1
        else:
            if node._suffix_link != tree.root:
                for leaf_node in get_leaf_nodes(tree, node):
                    suffix_index_of_leaf_node = leaf_node.idx
                    current_node.List_of_base_suffixes.append(suffix_index_of_leaf_node + 1)
                    base_suffix_counter += 1
                    cost += 1
    
       
    print ("Number of OSHR leaf_nodes is", "{:,}".format(OSHR_leaf_nodes_key_counter))
    print ("Number of OSHR internal nodes is", "{:,}".format(OSHR_internal_nodes_key_counter))
    print ("Total number of base suffixes", "{:,}".format(base_suffix_counter))
    print ("Total time cost:", "{:,}".format(cost))

   

start = time.time()
Find_base_suffixes_using_linear_algorithm(tree)
print ("Finished in", round((time.time() - start), 5), "seconds")
print ("------------------------------------------------------------------------------------------")
    

print ("Finding and checking base suffixes using the non-trivial algorithm 1 and O(n) space (hash-table)")

def Find_and_check_base_suffixes_using_non_trivial_algorithm1(tree):
    
    setattr(tree, "All_base_suffixes_found_so_far", defaultdict())
    cost = 0
    flag = 0
    
    nodes_stack = [(tree.root, False)]
    
    while nodes_stack:
        cost += 1
        current_node, visited = nodes_stack.pop()
        
        if not visited:
            # push back current node with visited=True (postorder processing)
            nodes_stack.append((current_node, True))
            
            # push children (to be processed first, since postorder)
            if hasattr(current_node, "List_of_nodes_suffix_linked_to_me"):
                for child_node in current_node.List_of_nodes_suffix_linked_to_me:
                    nodes_stack.append((child_node, False))
        else:
            if not current_node.is_leaf():
                d = []
                if hasattr(current_node, "List_of_nodes_suffix_linked_to_me"):
                    for leaf_node in get_leaf_nodes(tree, current_node):
                        cost += 1
                        suffix_index_of_leaf_node = leaf_node.idx
                        if suffix_index_of_leaf_node + current_node.depth not in tree.All_base_suffixes_found_so_far:
                            d.append(suffix_index_of_leaf_node + current_node.depth)
                            tree.All_base_suffixes_found_so_far[suffix_index_of_leaf_node + current_node.depth] = 0
                    
                else:
                    setattr(current_node, "All_suffixes_under_node", defaultdict())
                    for leaf_node in get_leaf_nodes(tree, current_node):
                        cost += 1
                        suffix_index_of_leaf_node = leaf_node.idx
                        tree.All_base_suffixes_found_so_far[suffix_index_of_leaf_node + current_node.depth] = 0
                        d.append(suffix_index_of_leaf_node + current_node.depth)

                        
                if sorted(d) != sorted(current_node.List_of_base_suffixes):
                    print ("The two base suffixes lists of this internal node are different", current_node, sorted(d), sorted(current_node.List_of_base_suffixes))   
                    flag = 1
             

    
    if flag == 0:
        print ("=== All base suffixes at each internal nodes in ST are as expected ===")
        print ("Total time cost:", "{:,}".format(cost))
    else:
        print ("*** There are base suffixes lists that are different at some internal nodes***")
    
    
start = time.time()    
Find_and_check_base_suffixes_using_non_trivial_algorithm1(tree)
print ("Finished in", round((time.time() - start), 5), "seconds")
print ("------------------------------------------------------------------------------------------")


 
print ("Finding and checking base suffixes using the non-trivial algorithm 2 with additional log(Sigma) time factor")

def Find_and_check_base_suffixes_using_non_trivial_algorithm2(tree):
    
    print ("Sorting nodes link through suffix-links to each node in ST")
    
    cost = 0
    
    nodes_stack = [(tree.root, False)]
    
    while nodes_stack:
        cost += 1
        current_node, visited = nodes_stack.pop()
        
        if not visited:
            # push back current node with visited=True (postorder processing)
            nodes_stack.append((current_node, True))
            
            # push children (to be processed first, since postorder)
            for child_node in current_node.transition_links.values():
                nodes_stack.append((child_node, False))   
        else:
            # alongside processing
            if not current_node.is_leaf():
                if hasattr(current_node, "List_of_nodes_suffix_linked_to_me"):
                    # The follwing new list will be needed in next phase
                    setattr(current_node, "List_of_nodes_suffix_linked_to_me_sorted_by_leaf_index_under_ST", [])
                    for node in current_node.List_of_nodes_suffix_linked_to_me:
                        current_node.List_of_nodes_suffix_linked_to_me_sorted_by_leaf_index_under_ST.append((node.index_of_leftmost_leaf_in_ST, node.index_of_rightmost_leaf_in_ST, node))
                        cost += 1
                    current_node.List_of_nodes_suffix_linked_to_me_sorted_by_leaf_index_under_ST.sort(key=lambda element: (element[0], element[1]))
                
            
    
    print ("Cost for sorting all List_of_nodes_suffix_linked_to_me", "{:,}".format(cost))
    
    # --------------------------------------------------------------------------- find base suffixes -------------------------------------------
    print ("Finding base suffixes")
    
    flag = 0
    
    nodes_stack = [(tree.root, False)]
    
    while nodes_stack:
        cost += 1
        current_node, visited = nodes_stack.pop()
        
        if not visited:
            # push back current node with visited=True (postorder processing)
            nodes_stack.append((current_node, True))
            
            # push children (to be processed first, since postorder)
            if hasattr(current_node, "List_of_nodes_suffix_linked_to_me"):
                for child_node in current_node.List_of_nodes_suffix_linked_to_me:
                    nodes_stack.append((child_node, False))

        else:
            cost += 1
            if not current_node.is_leaf():
                d = []
                if hasattr(current_node, "List_of_nodes_suffix_linked_to_me"):
                    for leaf_node in get_leaf_nodes(tree, current_node):
                        cost += int(math.log(len(current_node.List_of_nodes_suffix_linked_to_me_sorted_by_leaf_index_under_ST),2))
                        
                        f = 0
                        
                        suffix_index_of_leaf_node = leaf_node.idx
                        leaf_node_of_previous_suffix_index = tree.M[suffix_index_of_leaf_node - 1]
                        right_pos = bisect.bisect(current_node.List_of_nodes_suffix_linked_to_me_sorted_by_leaf_index_under_ST, (leaf_node_of_previous_suffix_index.index_of_leaf_in_ST, leaf_node_of_previous_suffix_index.index_of_leaf_in_ST)) # right_pos bcus we want to find node satisfies the condition starting_node.left_OT_index >= node.left_OT_index and starting_node.right_OT_index <= node.right_OT_index
                        if right_pos == len(current_node.List_of_nodes_suffix_linked_to_me_sorted_by_leaf_index_under_ST):
                            right_pos = right_pos - 1
                        node_suffix_link_to_current_node = current_node.List_of_nodes_suffix_linked_to_me_sorted_by_leaf_index_under_ST[right_pos][2]
                        if node_suffix_link_to_current_node.index_of_leftmost_leaf_in_ST <= leaf_node_of_previous_suffix_index.index_of_leaf_in_ST <= node_suffix_link_to_current_node.index_of_rightmost_leaf_in_ST:
                            f = 1
                        else:
                            right_pos = right_pos - 1
                            node_suffix_link_to_current_node = current_node.List_of_nodes_suffix_linked_to_me_sorted_by_leaf_index_under_ST[right_pos][2]
                            if node_suffix_link_to_current_node.index_of_leftmost_leaf_in_ST <= leaf_node_of_previous_suffix_index.index_of_leaf_in_ST <= node_suffix_link_to_current_node.index_of_rightmost_leaf_in_ST:
                                f = 1 
                        
                        if f == 0:
                            d.append(suffix_index_of_leaf_node + current_node.depth)
                    
                else:
                    for leaf_node in get_leaf_nodes(tree, current_node):
                        cost += 1
                        suffix_index_of_leaf_node = leaf_node.idx
                        d.append(suffix_index_of_leaf_node + current_node.depth)

                        
                if sorted(d) != sorted(current_node.List_of_base_suffixes):
                    print ("The two base suffixes lists of this internal node are different", current_node, sorted(d), sorted(current_node.List_of_base_suffixes))   
                    flag = 1
                    
                        


    if flag == 0:
        print ("=== All base suffixes at each internal nodes in ST are as expected ===")
        print ("Total time cost:", "{:,}".format(cost))
    else:
        print ("*** There are base suffixes lists that are different at some internal nodes***")
    
    
start = time.time()    
Find_and_check_base_suffixes_using_non_trivial_algorithm2(tree)
print ("Finished in", round((time.time() - start), 5), "seconds")








####### Not used: Algorithm for finding base suffixes using linear linear algorithm by creating explicitly reference leaf nodes and reference internal nodes (in case reference leaf nodes and reference internal nodes might be used)

def Find_base_suffixes_using_linear_algorithm2(tree):
    
    print ("Indexing reference_internal_nodes and reference_leaf_nodes")

    cost = 0
    OSHR_leaf_nodes_key_counter = 0
    OSHR_internal_nodes_key_counter = 0
    reference_internal_nodes = 0
    reference_leaf_nodes = 0
    
    nodes_stack = [(tree.root, False)]
    
    while nodes_stack:
        cost += 1
        current_node, visited = nodes_stack.pop()
        
        if not visited:
            # push back current node with visited=True (postorder processing)
            nodes_stack.append((current_node, True))
            
            # push children (to be processed first, since postorder)
            for child_node in current_node.transition_links.values():
                nodes_stack.append((child_node, False))   
        else:
            # alongside processing
            if current_node.is_leaf():
                # this code to find reference leaf nodes
                if current_node.idx + 1 < tree.number_leaf_nodes:
                    leaf_node_of_next_suffix_index = tree.M[current_node.idx + 1]                                    
                    if leaf_node_of_next_suffix_index.parent != current_node.parent._suffix_link:
                        n = leaf_node_of_next_suffix_index.parent
                        top_node = current_node.parent._suffix_link
                        
                        while True:
                            cost += 1
                            if n == top_node:
                                if current_node.parent == tree.root: # if so, then we must add this suffix as a base suffix to top_node unlike other cases (top_node must be tree.root)
                                    if not hasattr(n, "List_of_reference_leaf_nodes"):
                                        setattr(n, "List_of_reference_leaf_nodes", [])
                                    n.List_of_reference_leaf_nodes.append(current_node)
                                    reference_leaf_nodes += 1
                                break
                            else:
                                if not hasattr(n, "List_of_reference_leaf_nodes"):
                                    setattr(n, "List_of_reference_leaf_nodes", [])
                                n.List_of_reference_leaf_nodes.append(current_node)
                                n = n.parent
                                reference_leaf_nodes += 1

            else:
                #find and mark inbetween top base node and assign the reference nodes for this node (which are as coded below)
                if current_node._suffix_link.parent != current_node.parent._suffix_link:
                    top_node = current_node.parent._suffix_link 
                    bottom_node = current_node._suffix_link

                    n = bottom_node.parent
                    while n != top_node:
                        cost += 1
                        if not hasattr(n, "List_of_reference_internal_nodes"):
                            setattr(n, "List_of_reference_internal_nodes", [])
                        n.List_of_reference_internal_nodes.append(current_node)
                        n = n.parent
                        reference_internal_nodes += 1

                if hasattr(current_node, "List_of_nodes_suffix_linked_to_me"):
                    OSHR_internal_nodes_key_counter += 1
                else:
                    OSHR_leaf_nodes_key_counter += 1
                    


    print ("Number of OSHR leaf_nodes is", "{:,}".format(OSHR_leaf_nodes_key_counter))
    print ("Number of OSHR internal nodes is", "{:,}".format(OSHR_internal_nodes_key_counter))
    print ("Total number of reference_leaf_nodes", "{:,}".format(reference_leaf_nodes))
    print ("Total number of reference_internal_nodes", "{:,}".format(reference_internal_nodes))
    print ( "In total of", "{:,}".format(OSHR_leaf_nodes_key_counter + OSHR_internal_nodes_key_counter))
    print ("Cost for indexing reference_internal_nodes and reference_leaf_nodes:", "{:,}".format(cost))

    # --------------------------------------------------------------------------- find base suffixes -------------------------------------------
    
    print ("Finding base suffixes")
    
    base_suffix_counter = 0
    
    nodes_stack = [(tree.root, False)]
    
    while nodes_stack:
        cost += 1
        current_node, visited = nodes_stack.pop()
        
        if not visited:
            # push back current node with visited=True (postorder processing)
            nodes_stack.append((current_node, True))
            
            # push children (to be processed first, since postorder)
            for child_node in current_node.transition_links.values():
                nodes_stack.append((child_node, False))                                           
        else:
            # alongside processing
            if not current_node.is_leaf():
                #collect base suffixes derived from reference_leaf_node if any
                if hasattr(current_node, "List_of_reference_leaf_nodes"):
                    for reference_leaf_node in current_node.List_of_reference_leaf_nodes:
                        current_node.List_of_base_suffixes.append(reference_leaf_node.idx + 1 + current_node.depth)
                        base_suffix_counter += 1
                        cost += 1
                                                            
                #collect base suffixes derived from reference internal nodes if any
                if hasattr(current_node, "List_of_reference_internal_nodes"):
                    for reference_internal_node in current_node.List_of_reference_internal_nodes:
                        cost += 1
                        for leaf_node in get_leaf_nodes(tree, reference_internal_node):
                            cost += 1
                            suffix_index_of_leaf_node = leaf_node.idx
                            current_node.List_of_base_suffixes.append(suffix_index_of_leaf_node + 1 + current_node.depth)
                            base_suffix_counter += 1
                            

    # compute the case for suffix 0 as there is no previous suffix index for index 0 
    cost += 1
    temp = tree.M[0]                                     
    while temp != tree.root:
        temp = temp.parent
        temp.List_of_base_suffixes.append(0 + temp.depth)
        base_suffix_counter += 1
        cost += 1
            
    # this a special cases and for the root only. The suffix-link of child internal node of a root usually link to the root. In case not, 
    # then the node that the child internal node link to must be bottom-node for the root node.
    cost += 1
    current_node = tree.root
    for node in current_node.transition_links.values():
        cost += 1
        if node.is_leaf():
            if node.idx + 1 < tree.number_leaf_nodes:
                leaf_node_of_next_suffix_index = tree.M[node.idx + 1]
                if leaf_node_of_next_suffix_index.parent == tree.root:
                    current_node.List_of_base_suffixes.append(leaf_node_of_next_suffix_index.idx)
                    base_suffix_counter += 1
        else:
            if node._suffix_link != tree.root:
                for leaf_node in get_leaf_nodes(tree, reference_internal_node):
                    cost += 1
                    suffix_index_of_leaf_node = leaf_node.idx
                    current_node.List_of_base_suffixes.append(suffix_index_of_leaf_node + 1)
                    base_suffix_counter += 1

    
    print ("Total number of base suffixes", "{:,}".format(base_suffix_counter))
    print ("Total time cost:", "{:,}".format(cost))
    

#start = time.time()
#Find_base_suffixes_using_linear_algorithm2(tree)
#print ("Finished in", round((time.time() - start), 5), "seconds")
#print ("------------------------------------------------------------------------------------------")
     
