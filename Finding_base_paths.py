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



print ("Processing leaf and internal nodes")

def process_leaf_and_internal_nodes(tree):    
    setattr(tree, "number_leaf_nodes", 0)
    setattr(tree, "number_internal_nodes", 0)
     
    # stack entries are (node, visited_flag)
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
            # Now process the node (postorder stage)
            if current_node.is_leaf():
                # Assigning leaf nodes unique keys
                current_node.index_of_leaf_in_ST = tree.number_leaf_nodes                     
                tree.number_leaf_nodes += 1
                
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
                # construct implicit OSHR tree
                if current_node._suffix_link is not None and current_node != tree.root:
                    temp = current_node._suffix_link
                    if not hasattr(temp, "SLS"):
                        setattr(temp, "SLS", [])
                    temp.SLS.append(current_node)
            
                if not hasattr(current_node.parent, "index_of_leftmost_leaf_in_ST"):
                    setattr(current_node.parent, "index_of_leftmost_leaf_in_ST", current_node.index_of_leftmost_leaf_in_ST)
                elif current_node.index_of_leftmost_leaf_in_ST < current_node.parent.index_of_leftmost_leaf_in_ST:
                    current_node.parent.index_of_leftmost_leaf_in_ST = current_node.index_of_leftmost_leaf_in_ST
                    
                if not hasattr(current_node.parent, "index_of_rightmost_leaf_in_ST"):
                    setattr(current_node.parent, "index_of_rightmost_leaf_in_ST", current_node.index_of_rightmost_leaf_in_ST)
                elif current_node.index_of_rightmost_leaf_in_ST > current_node.parent.index_of_rightmost_leaf_in_ST:
                    current_node.parent.index_of_rightmost_leaf_in_ST = current_node.index_of_rightmost_leaf_in_ST
            
                # find and mark inbetween top base node and assign the reference nodes for this node
                if current_node._suffix_link.parent != current_node.parent._suffix_link:
                    top_node = current_node.parent._suffix_link 
                    bottom_node = current_node._suffix_link

                    n = bottom_node.parent
                    while n != top_node:
                        if not hasattr(n, "List_of_reference_internal_nodes"):
                            setattr(n, "List_of_reference_internal_nodes", [])
                        n.List_of_reference_internal_nodes.append(current_node)
                        n = n.parent

    print("Number of leaf nodes is", "{:,}".format(tree.number_leaf_nodes))
    print("Number of internal nodes is", "{:,}".format(tree.number_internal_nodes))
    print("Number of alphabets in the input data", len(tree.root.transition_links) - 1)


start = time.time()
process_leaf_and_internal_nodes(tree)
print ("Finished in", round((time.time() - start), 5), "seconds")
print ("------------------------------------------------------------------------------------------")
    

   
def get_internal_nodes(tree, node):
    results = []
    nodes_stack = [(node, False)]   # (node, visited flag)

    while nodes_stack:
        current_node, visited = nodes_stack.pop()

        if visited:
            # Now process after children
            if not current_node.is_leaf():
                results.append(current_node)
        else:
            # Push back the current_node node to process after children
            nodes_stack.append((current_node, True))

            # Push all children (sorted in reverse to keep left-to-right order)
            for child_node in current_node.transition_links.values():
                nodes_stack.append((child_node, False))

    # exclude the root (last in results due to postorder)
    return results[:-1]



print ("Finding base paths using the linear algorithm")

def Find_base_paths_using_linear_algorithm(tree):

    print ("Indexing OSHR leaf nodes into a list from left to right")
    
    setattr(tree, "List_of_OSHR_leaf_nodes_from_left_to_right", []) 
     
    cost = 0
    OSHR_leaf_nodes_key_counter = 0
    OSHR_internal_nodes_key_counter = 0

    # stack entries are (node, visited_flag)
    nodes_stack = [(tree.root, False)]
    
    while nodes_stack:
        cost += 1
        current_node, visited = nodes_stack.pop()
        
        if not visited:
            current_node.index_of_leftmost_OSHR_leaf = OSHR_leaf_nodes_key_counter
            
            # push back current node with visited=True (postorder processing)
            nodes_stack.append((current_node, True))
            
            # push children (to be processed first, since postorder)
            for child_node in current_node.transition_links.values():
                nodes_stack.append((child_node, False))
        else:
            # alongside processing
            if not current_node.is_leaf():
                # index OSHR leaf and OSHR internal nodes under ST internal nodes    
                if hasattr(current_node, "SLS"):
                    OSHR_internal_nodes_key_counter += 1
                    
                    # The follwing new list will be needed in next phase
                    setattr(current_node, "SLS_sorted_by_leaf_index_under_ST", [])
                    for node in current_node.SLS:
                        current_node.SLS_sorted_by_leaf_index_under_ST.append((node.index_of_leftmost_leaf_in_ST, node.index_of_rightmost_leaf_in_ST, node))
                        cost += 1
                    current_node.SLS_sorted_by_leaf_index_under_ST.sort(key=lambda element: (element[0], element[1]))
                
                else:
                    tree.List_of_OSHR_leaf_nodes_from_left_to_right.append(current_node)
                    OSHR_leaf_nodes_key_counter += 1
            
            
            current_node.index_of_rightmost_OSHR_leaf = OSHR_leaf_nodes_key_counter - 1

    print ("Number of OSHR leaf_nodes is", "{:,}".format(OSHR_leaf_nodes_key_counter))
    print ("Number of OSHR internal nodes is", "{:,}".format(OSHR_internal_nodes_key_counter))
    print ( "In total of", "{:,}".format(OSHR_leaf_nodes_key_counter + OSHR_internal_nodes_key_counter))
    print ("Cost for indexing OSHR leaf nodes into a list from left to right and sorting all SLS:", "{:,}".format(cost))
    
    # ------------------------------------------------------------------------ find base paths -------------------------------------------------------------------------
    print ("Finding base paths")
    
    base_paths_counter = 0
    a1, a2, b1, b2 = 0, 0, 0, 0
    
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
            # the following 6 lines cover a special case and for the root only. The suffix-link of child internal node of a root usually link to the root. In case not, 
            # then the node that the child internal node link to must be bottom-node for the root node.
            setattr(current_node, "List_of_bottom_base_node", [])
            if current_node != tree.root:
                if hasattr(current_node, "SLS"):
                    # collect and find base paths based on OSHR leaf nodes
                    for bottom_base_node in tree.List_of_OSHR_leaf_nodes_from_left_to_right[current_node.index_of_leftmost_OSHR_leaf:current_node.index_of_rightmost_OSHR_leaf + 1]:
                        current_node.List_of_bottom_base_node.append(bottom_base_node)
                        base_paths_counter += 1
                        a1 += 1
                        cost += 1
                    
                    # collect bottom-base nodes collected from reference nodes if current_node is List_of_reference_internal_nodes 
                    inbetween_bottom_base_node_dict = defaultdict(int)  # this dict will be used to distinct nodes under tow difference reference nodes that are linking to the same node under current_node                   
                    if hasattr(current_node, "List_of_reference_internal_nodes"):
                        for reference_node in current_node.List_of_reference_internal_nodes:
                            inbetween_bottom_base_node_dict[reference_node._suffix_link] += 1
                            cost += 1
                            for node in get_internal_nodes(tree, reference_node):
                                inbetween_bottom_base_node_dict[node._suffix_link] += 1
                                cost += 1
                            
                    for bottom_base_node in inbetween_bottom_base_node_dict:
                        cost += 1
                        if len(bottom_base_node.SLS) == inbetween_bottom_base_node_dict[bottom_base_node]:
                            a2 += 1
                            current_node.List_of_bottom_base_node.append(bottom_base_node)
                            base_paths_counter += 1
                        
                else:
                    for bottom_base_node in get_internal_nodes(tree, current_node):
                        current_node.List_of_bottom_base_node.append(bottom_base_node)
                        base_paths_counter += 1
                        cost += 1
                            
                        if hasattr(bottom_base_node, "SLS"):
                            b2 += 1
                        else:
                            b1 += 1
                            


    print ("Number of OSHR leaf bottom base nodes for OSHR internal top base nodes", "{:,}".format(a1))
    print ("Number of OSHR internal bottom base nodes for OSHR internal top base nodes", "{:,}".format(a2))
    print ("Number of OSHR leaf bottom base nodes for OSHR leaf top base nodes", "{:,}".format(b1))
    print ("Number of OSHR internal bottom base nodes for OSHR leaf top base nodes", "{:,}".format(b2))
    print ()
    print ("Total number of base paths", "{:,}".format(base_paths_counter))
    print ("Total time cost:", "{:,}".format(cost))
    
    
start = time.time()
Find_base_paths_using_linear_algorithm(tree)
print ("Finished in", round((time.time() - start), 5), "seconds")
print ("------------------------------------------------------------------------------------------")
    



def Find_and_check_base_paths_using_non_trivial_algorithm(tree):
    
    print ("Finding and checking base paths using the non-trivial algorithm")

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
            if hasattr(current_node, "SLS"):
                for child_node in current_node.SLS:
                    nodes_stack.append((child_node, False))

        else:
            if current_node != tree.root:
                if not current_node.is_leaf(): 
                    d = []
                    if hasattr(current_node, "SLS"):
                        for internal_node in get_internal_nodes(tree, current_node):
                            cost += 1
                            if hasattr(internal_node, "SLS"):
                                f = 0
                                for node_with_suffix_link_to_internal_node in internal_node.SLS:
                                    cost += int(math.log(len(current_node.SLS_sorted_by_leaf_index_under_ST),2)) 
                                    right_pos = bisect.bisect(current_node.SLS_sorted_by_leaf_index_under_ST, (node_with_suffix_link_to_internal_node.index_of_rightmost_leaf_in_ST, node_with_suffix_link_to_internal_node.index_of_rightmost_leaf_in_ST)) # right_pos bcus we want to find node satisfies the condition starting_node.left_OT_index >= node.left_OT_index and starting_node.right_OT_index <= node.right_OT_index
                                    if right_pos != 0:
                                        right_pos = right_pos - 1
                                    node_with_suffix_link_to_current_node = current_node.SLS_sorted_by_leaf_index_under_ST[right_pos][2]
                                    if node_with_suffix_link_to_current_node.index_of_leftmost_leaf_in_ST <= node_with_suffix_link_to_internal_node.index_of_leftmost_leaf_in_ST <= node_with_suffix_link_to_internal_node.index_of_rightmost_leaf_in_ST <= node_with_suffix_link_to_current_node.index_of_rightmost_leaf_in_ST:
                                        f = 1 
                                        break
                                                
                                if f == 0:
                                    d.append(internal_node)
                            else:
                                d.append(internal_node)
                    else:
                        for internal_node in get_internal_nodes(tree, current_node):
                            d.append(internal_node)
                            cost += 1
                
                        
                if sorted([str(x) for x in d]) != sorted([str(x) for x in current_node.List_of_bottom_base_node]):
                    print ("The two base paths lists of this internal node are different", current_node, tree._edgeLabel(current_node, tree.root), "\n", sorted([tree._edgeLabel(x, current_node) for x in d]), "\n", sorted([tree._edgeLabel(x, current_node) for x in current_node.List_of_bottom_base_node]))  
                    flag = 1


    if flag == 0:
        print ("=== All base paths at each internal nodes in ST are as expected ===")
        print ("Total time cost:", "{:,}".format(cost))
    else:
        print ("*** There are base paths lists that are different at some internal nodes***")
    
    
start = time.time()    
Find_and_check_base_paths_using_non_trivial_algorithm(tree)
print ("Finished in", round((time.time() - start), 5), "seconds")
   

 
