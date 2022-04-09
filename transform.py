import copy 

def graph_to_game(IOSM_graph):
    """graph_to_game transforms an IOSM (Input Output State Machine) graph into a finite directed bipartite graph.

    Args:
        IOSM_graph (tuple): IOSM graph, with structure (S, L, T, s0). S is a set of vertexes, L the transition language set and T a dictionnary of transitions between the vertexes. 
                            Structure of T is {'input vertex': [(output vertex, transition name)]}.
                            s0 is always equal to S[0].

    Returns:
        tuple:   FDB_graph: finite directed bipartite graph corresponding to the given IOSM graph, with structure (V, Vb, Vr, L, E, s0). V is a list of vertexes, Vb a list of vertexes 
                belonging to blue player (Vb included in V), Vr a list of vertexes belonging to red player (Vr included in V), L the transition language set, E a list of edges, and s0 
                equal to S[0]. Structure of E is (input vertex, transition name, output vertex).
    """

    _, L, T, s0 = IOSM_graph
    E = copy.deepcopy(T)

    color = {s0: 0}
    next = [s0]
    i = 0
    while len(next) > 0:
        n = next.pop()
        if n in E.keys():
            for neighbor, trans in E[n]:
                if neighbor not in color:
                    next.append(neighbor)
                    color[neighbor] = 1-color[n]
                elif color[neighbor] == color[n]:
                    new_node = "add"+str(i)

                    E[n].append((new_node, trans))
                    E[new_node] = [(neighbor, "tau")]
                    color[new_node] = 1-color[n]
                    i += 1

                    E[n].remove((neighbor, trans))

    Vb = set([x for x in color.keys() if color[x] == 0])
    Vr = set([x for x in color.keys() if color[x] == 1])

    FDB_graph = (Vb | Vr, Vb, Vr, L, E, s0)
    return FDB_graph


def obj_to_FDB_graph(obj, FDB_graph):
    '''
    Converts obj to the FDB_graph without creating another list

    Variables
        - obj : test objective to complete, a list of [(first vertex, transition name of L)] extracted from IOSM_graph
        - FDB_graph : finite directed bipartite graph corresponding to the given IOSM graph, with structure (V, Vb, Vr, L, E, s0)
    Returns :
        obj with vertices and "tau" transitions added when FDB_graph was built.
    '''
    (_, _, _, _, E, _) = FDB_graph
    for i, (node, trans) in enumerate(obj):
        for neigh, tr_node_to_neigh in E[node]:
            if tr_node_to_neigh == trans:
                if neigh[:3] == "add":
                    obj.insert(i+1, (neigh, "tau"))
    return obj


def add_fictif_point_init(ptAdded, transAdded, FDB_graph):
    '''
    Add a fictive point ptAdded that goes through transAdded to FDB_graph[-1]
    Remark : no need to link this red vertex to "puit"

    Variables :
        - ptAdded : name of the vertex created (str)
        - transAdded : name of the transition created from ptAdded to FDB_graph[-1] (with transAdded[0] == "?")
        - FDB_graph :  finite directed bipartite graph with structure (V, Vb, Vr, L, E, s0)
    Returns 
        - new_graph : finite directed bipartite graph with structure (V|{ptAdded}, Vb, Vr|{ptAdded}, L1, E1, s0), only ptAdded and transAdded are created
    '''
    assert transAdded[0] == "!"

    V, Vb, Vr, L, E, s0 = FDB_graph
    V |= {ptAdded}
    Vr |= {ptAdded}
    L |= {transAdded[1:]}

    E[ptAdded] = [(s0, transAdded)]

    return (V, Vb, Vr, L, E, s0)


if __name__ == '__main__':
    '''
    Useful not to run it when it's imported from another script
    '''

    S = {f"g{i}" for i in range(4)}
    L = set(["COIN", "BAD", "GOOD", "SODA", "CANCEL", "UNAV", "CAN"])
    T = {"g0": [("g1", "?COIN")], "g1": [("g0", "!BAD"), ("g2", "!GOOD")], "g2": [
        ("g3", "?SODA"), ("g0", "?CANCEL")], "g3": [("g2", "!UNAV"), ("g0", "!CAN")]}
    s0 = "g0"
    graph_test = (S, L, T, s0)
    FDB_graph = graph_to_game(graph_test)
    # print(FDB_graph)
    # print("obj =", obj_to_FDB_graph(
    #     [("g2", "?CANCEL")], FDB_graph))

    ptAdded = "fictPoint"
    transAdded = "!FICTRANS"
    fict_FDB_graph = add_fictif_point_init(ptAdded, transAdded, FDB_graph)

    # print(len(fict_FDB_graph))
