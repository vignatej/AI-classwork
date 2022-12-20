import unittest
import aima
import aima.core
from aima.core.agent import Action
import aima.core.search
from aima.core.search.framework import *
from aima.core.util.datastructure import LIFOQueue
from aima.core.search.framework import ActionFunction, ResultFunction, GoalTest

__author__ = 'Ivan Mushketik'

# Simple problem for testing
# Every state is a number. Action function generate 3 stub actions if state number is less then a specified limit
#

class TestAction(Action):
    def __init__(self):
        super().__init__("testAction")

    def is_noop(self):
        return False

class TestActionsFunction(ActionFunction):
    """
        Limit is specified to test failure and cutoffs in searches
    """
    def __init__(self, limit=None):
        self.limit = limit

    def actions(self, state):
        res = []

        if not self.limit or self.limit > state:
            for i in range(0, 3):
                res.append(TestAction())

        return res

class TestResultFunction(ResultFunction):
    def result(self, state, action):
        return state + 1

class TestGoalTest(GoalTest):
    def __init__(self, goal):
        self.goal = goal

    def is_goal_state(self, state):
        return state == self.goal

class TestNode(unittest.TestCase):

    def test_is_root_for_node_without_parent(self):
        n1 = Node("state1")
        self.assertTrue(n1.is_root_node(), "Node created without parent should be root")
        
    def test_is_root_for_node_with_parent(self):
        n1 = Node("state1")
        n2 = Node("state2", 0, n1)
        
        self.assertTrue(n1.is_root_node(), "Node created without parent should be root")
        self.assertFalse(n2.is_root_node(), "Node created with parent node shouldn't be root")
        self.assertEqual(n1, n2.get_parent(), "Node.getParent() is broken")
        
    def test_get_total_path_cost(self):
        n1 = Node("state1", 5)
        n2 = Node("state2", 10, n1)
        n3 = Node("state3", 15, n2)
                
        self.assertEqual(30, n3.get_path_cost(), "Path cost should be sum of cost of all nodes from root to a current node")
        
    def test_get_path_from_root(self):
        n1 = Node("state1", 5)
        n2 = Node("state2", 10, n1)
        n3 = Node("state3", 15, n2)
        
        path = n3.get_path_from_root()
        self.assertEquals(3, len(path), "Length of path should be equal to a number of nodes from current node to a root")
        self.assertEquals(n1, path[0])
        self.assertEquals(n2, path[1])
        self.assertEquals(n3, path[2])

class TestNodeExpander(unittest.TestCase):
    def test_node_expanding(self):
        startNode = Node(1)
        problem = Problem(1, TestActionsFunction(), TestResultFunction(), TestGoalTest(3))
        nodeExpander = NodeExpander()
        actionsList = nodeExpander.expand_node(startNode, problem)

        self.assertEqual(3, len(actionsList), "")
        self.assertEqual(2, actionsList[0].get_state())
        self.assertEqual(2, actionsList[1].get_state())
        self.assertEqual(2, actionsList[2].get_state())

class TestGraphSearch(unittest.TestCase):
    def test_successful_search(self):
        gs = GraphSearch()
        problem = Problem(1, TestActionsFunction(), TestResultFunction(), TestGoalTest(4))

        result = gs.search(problem, LIFOQueue())
        self.assertFalse(gs.is_failure(result))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()