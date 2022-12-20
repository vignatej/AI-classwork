from aima.core.search import utils
from aima.core.search.framework import Search, NodeExpander, Node, GraphSearch, PrioritySearch
from aima.core.util.datastructure import LIFOQueue, FIFOQueue
from aima.core.util.other import Comparator

__author__ = 'Ivan Mushketik'
__docformat__ = 'restructuredtext en'

 # Artificial Intelligence A Modern Approach (3rd Edition): Figure 3.11, page 82.
 #
 # function BREADTH-FIRST-SEARCH(problem) returns a solution, or failure
 #   node <- a node with STATE = problem.INITIAL-STATE, PATH-COST=0
 #   if problem.GOAL-TEST(node.STATE) then return SOLUTION(node)
 #   frontier <- a FIFO queue with node as the only element
 #   explored <- an empty set
 #   loop do
 #      if EMPTY?(frontier) then return failure
 #      node <- POP(frontier) // chooses the shallowest node in frontier
 #      add node.STATE to explored
 #      for each action in problem.ACTIONS(node.STATE) do
 #          child <- CHILD-NODE(problem, node, action)
 #          if child.STATE is not in explored or frontier then
 #              if problem.GOAL-TEST(child.STATE) then return SOLUTION(child)
 #              frontier <- INSERT(child, frontier)
 #
 # Figure 3.11 Breadth-first search on a graph.
class BreadthFirstSearch(Search):
    """
        Breadth fist search explores root and and then explores all nodes at level n before it starts to
        explore and node at level n + 1.

        This search can use any implementation of QueueSearch.
    """
    def __init__(self, search = GraphSearch()):
        self._search = search
        search.set_check_goal_before_adding_to_frontier(True)

    def search(self, problem):
        return self._search.search(problem, FIFOQueue())

    def get_metrics(self):
        return self._search.get_metrics()

 # Artificial Intelligence A Modern Approach (3rd Edition): Figure 3.14, page 84.
 #
 # function UNIFORM-COST-SEARCH(problem) returns a solution, or failure
 #   node <- a node with STATE = problem.INITIAL-STATE, PATH-COST = 0
 #   frontier <- a priority queue ordered by PATH-COST, with node as the only element
 #   explored <- an empty set
 #   loop do
 #      if EMPTY?(frontier) then return failure
 #      node <- POP(frontier) // chooses the lowest-cost node in frontier
 #      if problem.GOAL-TEST(node.STATE) then return SOLUTION(node)
 #      add node.STATE to explored
 #      for each action in problem.ACTIONS(node.STATE) do
 #          child <- CHILD-NODE(problem, node, action)
 #          if child.STATE is not in explored or frontier then
 #             frontier <- INSERT(child, frontier)
 #          else if child.STATE is in frontier with higher PATH-COST then
 #             replace that frontier node with child
class UniformCostSearch(PrioritySearch):
    """
        This search explores nodes with the lowest search path cost first.
    """
    def __init__(self, queue_search = None):
        if queue_search == None:
            queue_search = GraphSearch()

        super().__init__(queue_search)

    def _get_comparator(self):
        class PathCostComparator(Comparator):
            def compare(self, node1, node2):
                pass

        return PathCostComparator()


# Artificial Intelligence A Modern Approach (3rd Edition): page 85.
class DepthFirstSearch(Search):
    """
        Depth first search examines first expanded node and checks if it's state is a goal state.
        If not, it expands it and examines first expanded node.

        This search can use any implementation of QueueSearch.
    """
    def __init__(self, queueSearch):
        self._search = queueSearch

    def search(self, problem):
        return self._search.search(problem, LIFOQueue())

    def get_metrics(self):
        return self._search.get_metrics()

# Artificial Intelligence A Modern Approach (3rd Edition): Figure 3.17, page 88

 # function DEPTH-LIMITED-SEARCH(problem, limit) returns a solution, or failure/cutoff
 #   return RECURSIVE-DLS(MAKE-NODE(problem.INITIAL-STATE), problem, limit)
 #
 # function RECURSIVE-DLS(node, problem, limit) returns a solution, or failure/cutoff
 #   if problem.GOAL-TEST(node.STATE) then return SOLUTION(node)
 #   else if limit = 0 then return cutoff
 #   else
 #       cutoff_occurred? <- false
 #       for each action in problem.ACTIONS(node.STATE) do
 #           child <- CHILD-NODE(problem, node, action)
 #           result <- RECURSIVE-DLS(child, problem, limit - 1)
 #           if result = cutoff then cutoff_occurred? <- true
 #           else if result != failure then return result
 #       if cutoff_occurred? then return cutoff else return failure
class DepthLimitedSearch(NodeExpander, Search):
    PATH_COST = "pathCost"

    def __init__(self, limit):
        super().__init__()
        self._limit = limit
        self._metrics[DepthLimitedSearch.PATH_COST] = 0

    def clear_instrumentation(self):
        super().clear_instrumentation()
        self._metrics[DepthLimitedSearch.PATH_COST] = 0

    def get_path_cost(self):
        return self._metrics[DepthLimitedSearch.PATH_COST]

    def set_path_cost(self, path_cost):
        self._metrics[DepthLimitedSearch.PATH_COST] = path_cost

    def get_metrics(self):
        return self._metrics

    def search(self, problem):
        """
            Search solution for a problem with Depth First Search strategy with a specified depth limit.

            problem - problem to find solution for
            returns list of actions to execute from initial state to reach goal state. If search failed return a list that
            represents failure. If search ended because of cutoff returns a list that represents that cutoff occurred
        """

        # return RECURSIVE-DLS(MAKE-NODE(INITIAL-STATE[problem]), problem, limit)
        return self._recursive_dls(Node(problem.get_initial_state()), problem, self._limit)

    def _recursive_dls(self, curNode, problem, limit):

        # if problem.GOAL-TEST(node.STATE) then return SOLUTION(node)
        if utils.is_goal_state(problem, curNode):
            self.set_path_cost(curNode.get_path_cost())
            return utils.actions_from_nodes(curNode.get_path_from_root())
        elif limit == 0:
            # else if limit = 0 then return cutoff
            return self._cutoff()
        else:
            # else
			# cutoff_occurred? <- false
            childNodes = self.expand_node(curNode, problem)

            cutoff_occurred = False
            # for each action in problem.ACTIONS(node.STATE) do
            for node in childNodes:
                # child <- CHILD-NODE(problem, node, action)
				# result <- RECURSIVE-DLS(child, problem, limit - 1)
                result = self._recursive_dls(node, problem, limit - 1)

                # if result = cutoff then cutoff_occurred? <- true
                if self.is_cutoff(result):
                    cutoff_occurred = True
                elif not self.is_failure(result):
                    # else if result != failure then return result
                    return result

            # if cutoff_occurred? then return cutoff else return failure
            if cutoff_occurred:
                return self._cutoff()
            else:
                return self._failure()




# Artificial Intelligence A Modern Approach (3rd Edition): Figure 3.18, page 89.
#
# function ITERATIVE-DEEPENING-SEARCH(problem) returns a solution, or failure
#   for depth = 0 to infinity  do
#     result <- DEPTH-LIMITED-SEARCH(problem, depth)
#     if result != cutoff then return result
class IterativeDeepeningSearch(Search):
    """
        Iterative Deepening search works file limited DFS, but instead it increases search limit. If search failed to
        find solution at selected depth or if solution was found search terminates. If cutoff occurred depth limit is
        increased.
    """
    PATH_COST = "pathCost"
    METRICS_NODES_EXPANDED = "nodesExpanded"

    def __init__(self):
        self._metrics = {}
        self.clear_instrumentation()

    def clear_instrumentation(self):
        self._metrics[self.PATH_COST] = 0
        self._metrics[self.METRICS_NODES_EXPANDED] = 0

    # function ITERATIVE-DEEPENING-SEARCH(problem) returns a solution, or failure
    def search(self, problem):
        self.clear_instrumentation()

        currLimit = 0
        # for depth = 0 to infinity do
        while True:
            # result <- DEPTH-LIMITED-SEARCH(problem, depth)
            dls = DepthLimitedSearch(currLimit)
            result = dls.search(problem)

            self._metrics[self.METRICS_NODES_EXPANDED] = self._metrics[self.METRICS_NODES_EXPANDED] + \
                                                         dls.get_metrics()[DepthLimitedSearch.METRIC_NODES_EXPANDED]

            # if result != cutoff then return result
            if not dls.is_cutoff(result):
                self._metrics[self.PATH_COST] = dls.get_path_cost()
                return result

            currLimit = currLimit + 1

    def get_metrics(self):
        return self._metrics


