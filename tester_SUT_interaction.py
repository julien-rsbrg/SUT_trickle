from choice_to_make import choose_transition, dico_W
from objective_creation import existChemin
from transform import graph_to_game, obj_to_FDB_graph, add_fictif_point_init
from objective_creation import randomObjectifTest
import os
import sys
import datetime
import random

# start to read at start_machine(...)
# command() of IOController to change()


def simulate_non_determinism():
    '''
    Change it for a denser tree (with more than 2 choices max per vertex)
    '''
    return random.choice([True, False])


class SystemSignatureViolation(Exception):
    pass


class IATesteurError(Exception):
    pass


class TestOver(Exception):
    pass


class ObjectiveNotCompatible(Exception):
    pass


class TimeOut(Exception):
    pass


def can_loop(io_controller, adv, position=None, FDB_graph=None):
    if adv.testOver():
        raise TestOver()
    ev_name = io_controller.get_input(adv)
    if(ev_name == "SODA"):
        g = simulate_non_determinism()
        if g:
            car = "CAN"
            io_controller.transition = car
            io_controller.write_output(car)
            return False
        else:
            car = "UNAV"
            io_controller.transition = car
            io_controller.write_output(car)
            return True
    elif(ev_name == "CANCEL"):
        if adv.name == "IATesteur":
            # only matters to share tau artificial output in this case
            car = "tau"
            io_controller.transition = car
            io_controller.write_output(car)
        return False
    else:
        raise SystemSignatureViolation()


def coin_loop(io_controller, adv):
    if adv.testOver():
        raise TestOver()

    ev_name = io_controller.get_input(adv)
    if(ev_name == "COIN"):
        g = simulate_non_determinism()
        if g:
            car = 'GOOD'
            io_controller.transition = car
            io_controller.write_output(car)
            while(g):
                g = can_loop(io_controller, adv)
        else:
            car = "BAD"
            io_controller.transition = car
            io_controller.write_output(car)
    else:
        raise SystemSignatureViolation()


def start_machine(io_controller, adv):
    '''
    Variables :
     - io_controller : SUT to test
     - adv : test operator
    '''

    while(True):
        coin_loop(io_controller, adv)


class IOController(object):
    '''
    Modified in order to inform the test where the system is 
    '''

    def __init__(self, transAdded):
        self.transition = transAdded[1:]
        self.terminal = sys.stdout
        current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        self.log = open("boisson_record_%s.log" % current_time, "a")

    def write_output(self, message):
        if not message.endswith(os.linesep):
            message += os.linesep
        # self.terminal.write(message)
        self.log.write(message)

    def get_input(self, adv):
        got = adv.command(self.transition)
        if not got.endswith(os.linesep):
            self.log.write(got + os.linesep)
        else:
            self.log.write(got)
        return got


class HumanPlayer(object):
    def __init__(self):
        self.name = "human"
        self.transition = None
        self.Obj_Reached = False
        self.position = None

    def command(self, transition):
        print(transition)
        self.transition = input()
        return self.transition

    def testOver(self):
        return False


def deduce_next_position(pos, ext_trans, FDB_graph):
    '''

    Returns :
        - next_pos : the vertex at the end of the transition starting from pos named ext_trans
    '''
    # set the new position
    found_trans = False
    next_pos = None
    bool_tau = (ext_trans[1:] == "tau")
    if bool_tau:
        ext_trans = ext_trans[1:]
    for neigh, trans in FDB_graph[4][pos]:
        if trans == ext_trans:
            if bool_tau:
                return neigh
            elif found_trans:
                # force unique possibility
                raise SystemSignatureViolation()
            found_trans = True
            next_pos = neigh
    if next_pos == None:
        print("IATesteur is blocked on a vertex.")
        raise IATesteurError()
    return next_pos


class IATesteur(object):
    '''
    Aims to test online another system with its results compared to a FDB graph where transition are strings with the first caracter being ! or ?
    '''

    def __init__(self, obj, FDB_graph, ptAdded, Nmax_transitions):
        '''
        Variables :
            - obj : test objective to complete, a list of [(first vertex, transition name of L)] extracted from IOSM_graph
            - FDB_grah (tuple) : finite directed bipartite graph with structure (V, Vb, Vr, L, E, s0)
            - ptAdded (str) : the fictive point added before the beginning for the initialisation
        '''
        self.name = "IATesteur"
        self.position = ptAdded  # fictive point
        self.FDB_graph = FDB_graph
        self.counter = 0
        self.Nmax_transitions = Nmax_transitions
        new_obj = obj_to_FDB_graph(obj, self.FDB_graph)
        if existChemin(new_obj, FDB_graph, IOSM_is_graph_type=False):
            self.objective = new_obj
        else:
            print("obj_to_FDB_graph is not working")
            raise ObjectiveNotCompatible()
        self.completion = []
        self.dict_W = {}  # to change
        self.Obj_Reached = (self.completion == self.objective)

        # for empty objective
        if self.testOver():
            raise TestOver()

    def testOver(self):
        return self.Obj_Reached and self.position == self.FDB_graph[-1]

    def update_comp(self, pos, trans):
        '''
        1) DO NOT Change position of IATesteur
        2) Add (pos,trans) to self.completion if next element in objective
        3) Set self.completion = [] if the test gets out of the objective
        4) Set self.dict_W = {} if IATesteur is in the objective

        Variables :
            -pos : the vertex from which tran starts (str) (ex: "g0")
            -trans : the transition name one of the player just passed through (str) (ex : "!COIN")
        '''

        if not(self.Obj_Reached):
            # second  == to adapt if the punctuation is kept or not
            if pos == self.objective[len(self.completion)][0] and trans == self.objective[len(self.completion)][1]:
                if not(len(self.completion)):
                    # not to go in here too often, first time you go in completion
                    self.dict_W = {}
                self.completion.append((pos, trans))
            else:
                if len(self.dict_W.keys()):
                    # first time you get out of the objective
                    self.dict_W = dico_W(self.objective[0][0], self.FDB_graph)
                self.completion = []
            self.Obj_Reached = (self.completion == self.objective)

    def command(self, io_transition):
        '''
        Returns a command to complete IATesteur objective, it needs position, completion, dict_W, Obj_Reached updated
        by the SUT, while playing


        '''
        self.counter += 1

        if self.counter > self.Nmax_transitions:
            raise TimeOut()
        obj = self.objective
        dict_W = self.dict_W

        # set if the objective is reached
        if io_transition == "tau":
            self.update_comp(self.position, io_transition)
        else:
            self.update_comp(self.position, "!"+io_transition)

        if self.testOver():
            raise TestOver()

        # set new position
        self.position = deduce_next_position(
            self.position, "!"+io_transition, self.FDB_graph)

        trans_next = None
        # continue the completion of the objective, once its completion has begun
        if not(self.Obj_Reached) and self.position == obj[len(self.completion)][0]:
            trans_next = obj[len(self.completion)][1]
            pos_next = deduce_next_position(
                self.position, trans_next, self.FDB_graph)
            self.update_comp(self.position, trans_next)
            self.position = pos_next

        # get to the first point of objective, when it is not reached
        elif not(self.Obj_Reached) and not(len(self.completion)):
            if not(len(dict_W)):
                dict_W = dico_W(obj[0][0], self.FDB_graph)
            # not empty anymore
            pos_next, trans_next = choose_transition(
                self.position, self.FDB_graph, dict_W)
            # in order (current position, trans_next), (pos_next, ...) if alright with objective
            self.update_comp(self.position, trans_next)
            self.position = pos_next

        # return to the first point of departure, once the objective is completed
        if self.Obj_Reached and self.position != self.FDB_graph[-1]:
            if not(len(dict_W)):
                dict_W = dico_W(self.FDB_graph[-1], self.FDB_graph)
            pos_next, trans_next = choose_transition(
                self.position, self.FDB_graph, dict_W)
            # no need to update as the method is to reach the completion of the objective
            self.position = pos_next

        if self.testOver():
            raise TestOver()

        if trans_next == None:
            raise IATesteurError()
        self.transition = trans_next[1:]
        return trans_next[1:]


def test_series(IOSM_graph, Nmax_transitions=40, l_obj=[], N_obj=2, D_obj=6):
    '''
    It checks each test objective of l_obj on an SUT (in this .py file, a vending machine). 
    If no objective is given, it randomly creates N_obj test objectives, of length from 1 to D_obj 

    Variables : 
        - IOSM_graph (tuple): IOSM graph, with structure (S, L, T, s0). S is a set of vertexes, L the transition language set and T a dictionnary of transitions between the vertexes. 
                       Structure of T is {'input vertex': [(output vertex, transition name)]}.
                       s0 is always equal to S[0].
        - l_obj (list): a list of test objectives, each test objective being a list of the form [(node0, transition from node0),...]
        - N_obj (int): the lenght of the list of objectives automatically created if l_obj is not given or empty
        - D_obj (int): the maximum length of an objective of the automatically created objectives
    '''
    FDB_graph = graph_to_game(IOSM_graph)
    ptAdded = "fictPoint"
    transAdded = "!FICTRANS"
    FDB_graph = add_fictif_point_init(ptAdded, transAdded, FDB_graph)
    print("deduced FDB graph  :")
    print("V, Vb, Vr : ", FDB_graph[:3])
    print("L : ", FDB_graph[3])
    print("E : ", FDB_graph[4])
    print("s0 : ", FDB_graph[5])
    io_controller = IOController(transAdded)

    if not len(l_obj):
        for _ in range(N_obj):
            d = random.randint(1, D_obj)
            l_obj.append(randomObjectifTest(IOSM_graph, d))

    for obj in l_obj:
        if not existChemin(obj, IOSM_graph):
            io_controller.write_output(str(obj))
            raise ObjectiveNotCompatible()
        test_obj(obj, io_controller, ptAdded, transAdded, FDB_graph)


def test_obj(obj, io_controller, ptAdded, transAdded, FDB_graph, Nmax_transitions=40,):
    adv = IATesteur(obj, FDB_graph, ptAdded, Nmax_transitions)
    io_controller.transition = transAdded[1:]
    io_controller.write_output(str(obj))
    try:
        start_machine(io_controller, adv)
    except SystemSignatureViolation:
        io_controller.write_output("ABORT")
    except TestOver:
        io_controller.write_output("TEST SUCCEEDS")
    except IATesteurError:
        io_controller.write_output(
            "IATesteur FAILED, IT DID NOT FIND THE NEXT POSITION OR TRANSITION")
    except ObjectiveNotCompatible:
        io_controller.write_output(str(obj))
        io_controller.write_output(
            "THE OBJECTIVE AND THE IOSM GRAPH ARE NOT CONSISTENT TOGETHER")
    except TimeOut:
        io_controller.write_output(str(obj))
        io_controller.write_output("THE TEST TOOK TOO LONG")


def run_human():
    io_controller = IOController("")
    adv = HumanPlayer()
    try:
        start_machine(io_controller, adv)
    except SystemSignatureViolation:
        io_controller.write_output("ABORT")


if __name__ == '__main__':
    S = {f"g{i}" for i in range(4)}
    L = set(["COIN", "BAD", "GOOD", "SODA", "CANCEL", "UNAV", "CAN"])
    T = {"g0": [("g1", "?COIN")], "g1": [("g0", "!BAD"), ("g2", "!GOOD")], "g2": [
        ("g3", "?SODA"), ("g0", "?CANCEL")], "g3": [("g2", "!UNAV"), ("g0", "!CAN")]}
    s0 = "g0"
    IOSM_graph = (S, L, T, s0)

    # run_human()  #SUT anwer GOOD to CANCEL
    test_series(IOSM_graph)
