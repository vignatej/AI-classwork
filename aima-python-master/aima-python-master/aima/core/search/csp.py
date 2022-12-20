from abc import ABCMeta
from aima.core.util.datastructure import FIFOQueue
from aima.core.util.functions import select_randomly_from_list
from aima.core.util.other import PlusInfinity

__author__ = 'Ivan Mushketik'
__docformat__ = 'restructuredtext en'

class Variable:
    """
    Variable is an object with unique name.
    """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "CSPVariable('" + str(self.name) + "')"

    def __eq__(self, other):
        if not isinstance(other, Variable):
            return False

        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


class Domain:
    """
    Defines set of values that can be assigned to a variable
    """
    def __init__(self, values):
        """

        :param values (list): values that can be assigned
        :return:
        """
        self.values = list(values)

    def size(self):
        """
        Get number of values in domain

        :return (int): number of values
        """
        return len(self.values)

    def get(self, index):
        """
        Get value with specified number

        :param index: number of value in domain
        :return: value from the domain
        """

        return self.values[index]

    def remove(self, value):
        """
        Remove value from domain

        :param value: value to remove
        :return: None
        """
        self.values.remove(value)

    def is_empty(self):
        """
        Check if domain is empty

        :return (bool): True if domain is empty, False otherwise
        """
        return len(self.values) == 0

    def contains(self, value):
        """
        Check if specified value belongs to a domain

        :param value: value to check
        :return (bool): True if value belongs to a domain, False otherwise
        """
        return value in self.values

    def __iter__(self):
        return iter(self.values)

    def __eq__(self, other):
        if not isinstance(other, Domain):
            return False

        if self.size() != other.size():
            return False

        for i in range(self.size()):
            if self.get(i) != other.get(i):
                return False

        return True

    def __str__(self):
        return str(self.values)


class Assignment:
    """
    This class holds what values was assigned to what variables
    """
    def __init__(self):
        self.variable_to_value = {}

    def get_variables(self):
        """
        Get assigned variables

        :return list(Variable): list of assigned variables
        """
        return self.variable_to_value.keys()

    def get_assignment(self, var):
        """
        Get value that was assigned to the specified variable

        :param var (Variable):
        :return: assigned value if any was assigned to a specified variable, None otherwise
        """
        return self.variable_to_value.get(var)

    def set_assignment(self, var, value):
        """
        Assign valut to a variable

        :param var: variable to assign
        :param value: value to assign
        :return: None
        """
        self.variable_to_value[var] = value

    def remove_assignment(self, var):
        """
        Remove assignment for a specified variable

        :param var (Variable): variable to remove assignment for
        :return: None
        """

        del self.variable_to_value[var]

    def has_assignment_for(self, var):
        """
        Check if any value was assigned to a specified variable

        :param var (Variable): variable to check
        :return: True if some value was assigned, false otherwise
        """
        return self.variable_to_value.get(var) != None

    def is_consistent(self, constraints):
        """
        Check if current assignment doesn't violate any constraint

        :param constraints (Constraint): constraints to check
        :return (bool): True all constrainsts are satisfied, False otherwise 
        """
        for constraint in constraints:
            if not constraint.is_satisfied_with(self):
                return False
        return True

    def is_complete(self, variables):
        """
        Check if all values were assigned to all variables.

        :param variables iterable(Variables): variables to check
        :return (bool): True if values were assigned to all variables, False otherwise
        """
        for var in variables:
            if not self.has_assignment_for(var):
                return False

        return True

    def is_solution(self, csp):
        """
        Check if current assignment is a solution to the specifed CSP problem

        :param csp (CSP):
        :return (bool): True is current assignment is a solution, False otherwise.
        """
        return self.is_consistent(csp.get_constraints()) and self.is_complete(csp.get_variables())

    def copy(self):
        copy = Assignment()
        copy.variable_to_value = self.variable_to_value.copy()

        return copy

    def __str__(self):
        first = True
        result = "{"
        for var in self.variable_to_value.keys():
            if not first:
                result += ", "
            result += str(var) + " = " + str(self.variable_to_value[var])
            first = False

        result += "}"
        return result


class Constraint(metaclass=ABCMeta):
    """
    Abstract class for specifying a constraint in CSP problem
    """
    def get_scope(self):
        """
        Get variables that are constrained by an instance of this class

        :return iterable(Variable):
        """
        raise NotImplementedError()

    def is_satisfied_with(self, assignment):
        raise NotImplementedError()

class NotEqualConstraint(Constraint):
    def __init__(self, var1, var2):
        self.var1 = var1
        self.var2 = var2
        self.scope = (var1, var2)

    def get_scope(self):
        return self.scope

    def is_satisfied_with(self, assignment):
        value1 = assignment.get_assignment(self.var1)

        return value1 == None or (not value1 == assignment.get_assignment(self.var2))


class CSP:

    def __init__(self, variables):
        self.variables = list(variables)
        self.domains = {}
        self.constraints = []
        self.var_constraints = {}

        for variable in variables:
            self.domains[variable] = []
            self.var_constraints[variable] = []

    def get_variables(self):
        return self.variables

    def get_domain(self, var):
        return self.domains[var]

    def set_domain(self, var, domain):
        self.domains[var] = Domain(domain.values)

    def remove_value_from_domain(self, var, value):
        self.domains[var].remove(value)


    def get_constraints(self, var=None):
        if var != None:
            return self.var_constraints[var]
        else:
            return self.constraints

    def add_constraint(self, constraint):
        self.constraints.append(constraint)
        for var in constraint.get_scope():
            self.var_constraints[var].append(constraint)

    def get_neighbor(self, var, constraint):
        pass

    def copy_domains(self):
        result = CSP()
        result.constraints = list(self.constraints)
        result.var_constraints = self.var_constraints.copy()
        result.domains = self.domains.copy()
        

class CSPStateListener(metaclass=ABCMeta):
    def state_changed(self, csp, assignment):
        raise NotImplementedError()


class SolutionStrategy:
    def __init__(self):
        self.listeners = []

    def add_csp_state_listener(self, listener):
        self.listeners.append(listener)

    def remove_csp_state_listener(self, listener):
        self.listeners.remove(listener)

    def _notify_state_changed(self, csp, assignment=None):
        for listener in self.listeners:
            listener.state_changed(csp, assignment)

    def solve(self, csp):
        raise NotImplementedError()


class DomainRestoreInfo:
    def __init__(self):
        self.saved_domains = {}
        self.empty_domain_found = False

    def clear(self):
        self.saved_domains = {}

    def is_empty(self):
        return len(self.saved_domains.keys()) == 0

    def store_domain_for(self, var, domain):
        if self.saved_domains.get(var) == None:
            self.saved_domains[var] = list(domain)

    def restore_domains(self, csp):
        for var in self.saved_domains.keys():
            csp.set_domain(var, self.saved_domains[var])


        
    
# Artificial Intelligence A Modern Approach (3rd Ed.): Figure 6.5, Page 215.
# 
#
# function BACKTRACKING-SEARCH(csp) returns a solution, or failure
#    return BACKTRACK({ }, csp)
# 
# function BACKTRACK(assignment, csp) returns a solution, or failure
#    if assignment is complete then return assignment
#    var = SELECT-UNASSIGNED-VARIABLE(csp)
#    for each value in ORDER-DOMAIN-VALUES(var, assignment, csp) do
#       if value is consistent with assignment then
#         add {var = value} to assignment
#         inferences = INFERENCE(csp, var, value)
#         if inferences != failure then
#             add inferences to assignment
#             result = BACKTRACK(assignment, csp)
#             if result != failure then
#                return result
#         remove {var = value} and inferences from assignment
#    return failure
# 
# Figure 6.5 A simple backtracking algorithm for constraint satisfaction
# problems. The algorithm is modeled on the recursive depth-first search of
# Chapter 3. By varying the functions SELECT-UNASSIGNED-VARIABLE and
# ORDER-DOMAIN-VALUES, we can implement the general-purpose heuristic discussed
# in the text. The function INFERENCE can optionally be used to impose arc-,
# path-, or k-consistency, as desired. If a value choice leads to failure
# (noticed wither by INFERENCE or by BACKTRACK), then value assignments
# (including those made by INFERENCE) are removed from the current assignment
# and a new value is tried.
class BacktrackingStrategy(SolutionStrategy):
    # function BACKTRACKING-SEARCH(csp) returns a solution, or failure
    # return BACKTRACK({ }, csp)
    def solve(self, csp):
        return self._recursive_backtrack_search(csp, Assignment())

    # function BACKTRACK(assignment, csp) returns a solution, or failure
    def _recursive_backtrack_search(self, csp, assignment):
        result = None
        # if assignment is complete then return assignment
        if assignment.is_complete(csp.get_variables()):
            result = assignment
        else:
            # var = SELECT-UNASSIGNED-VARIABLE(csp)
            var = self._select_unassigned_variable(assignment, csp)
            # for each value in ORDER-DOMAIN-VALUES(var, assignment, csp) do
            for value in self._order_domain_values(var, csp, assignment):
                # add {var = value} to assignment
                assignment.set_assignment(var, value)
                # inferences = INFERENCE(csp, var, value)
                # if inferences != failure then
                if assignment.is_consistent(csp.get_constraints(var)):
                    info = self._inference(var, assignment, csp)

                    if not info.is_empty():
                        self._notify_state_changed(csp)
                    if not info.empty_domain_found:
                        # result = BACKTRACK(assignment, csp)
                        result = self._recursive_backtrack_search(csp, assignment)
                        # if result != failure then
                        if result != None:
                            # return result
                            break

                    info.restore_domains(csp)
                # remove {var = value} and inferences from assignment
                assignment.remove_assignment(var)

        return result

    def _select_unassigned_variable(self, assignment, csp):
        """
        Select one of unassigned variables. This method is overridden in ImprovedBacktrackingStrategy
        to implement different variable selection heuristics

        :param assignment (Assignment): current assignment
        :param csp (CSP): CSP to solve
        :return (Variable): variable to assign value for
        """
        for var in csp.get_variables():
            if not assignment.has_assignment_for(var):
                return var

        return None

    def _order_domain_values(self, var, csp, assignment):
        return csp.get_domain(var)

    def _inference(self, var, assignment, csp):
        return DomainRestoreInfo()


# Artificial Intelligence A Modern Approach (3rd Ed.): Figure 6.3, Page 209.
# 
#
# function AC-3(csp) returns false if an inconsistency is found and true otherwise
#    inputs: csp, a binary CSP with components (X, D, C)
#    local variables: queue, a queue of arcs, initially all the arcs in csp
#    while queue is not empty do
#       (Xi, Xj) = REMOVE-FIRST(queue)
#       if REVISE(csp, Xi, Xj) then
#          if size of Di = 0 then return false
#             for each Xk in Xi.NEIGHBORS - {Xj} do
#                add (Xk, Xi) to queue
#    return true
# 
# function REVISE(csp, Xi, Xj) returns true iff we revise the domain of Xi
#    revised = false
#    for each x in Di do
#       if no value y in Dj allows (x ,y) to satisfy the constraint between Xi and Xj then
#          delete x from Di
#          revised = true
#    return revised
# 
# Figure 6.3 The arc-consistency algorithm AC-3. After applying AC-3, either
# every arc is arc-consistent, or some variable has an empty domain, indicating
# that the CSP cannot be solved. The name "AC-3" was used by the algorithm's
# inventor (Mackworth, 1977) because it's the third version developed in the
# paper.
class AC3Strategy:
    def reduce_domains(self, csp, var=None, value=None, assignment=None):
        if var == None:
            result = DomainRestoreInfo()
            queue = FIFOQueue()
            for var in csp.get_variables():
                queue.add(var)

            self._reduce_domains(queue, csp, result, Assignment())
            return result

        else:
            result = DomainRestoreInfo()
            domain = csp.get_domain(var)
            if  domain.contains(value):
                if domain.size() > 1:
                    queue = FIFOQueue()
                    queue.add(var)
                    result.store_domain_for(var, domain)
                    csp.set_domain(var, Domain([value]))
                    self._reduce_domains(queue,csp, result, assignment)
            else:
                result.empty_domain_found = True

            return result

    def _reduce_domains(self, queue, csp, info, assignment):
        while not queue.is_empty():
            var = queue.pop()

            for constraint in csp.get_constraints(var):
                neighbors = set([n for n in constraint.get_scope() if n != var ])
                for neighbor in neighbors:
                    if self._revise(neighbor, var, constraint, csp, info, assignment):
                        if csp.get_domain(neighbor).is_empty():
                            info.empty_domain_found = True
                            return
                        queue.add(neighbor)

    def _revise(self, xi, xj, constraint, csp, info, assignment):
        revised = False
        copy_assignment = assignment.copy()

        for i_value in csp.get_domain(xi):
            copy_assignment.set_assignment(xi, i_value)
            consistent_extension_found = False

            for j_value in csp.get_domain(xj):
                copy_assignment.set_assignment(xj, j_value)
                if constraint.is_satisfied_with(copy_assignment):
                    consistent_extension_found = True
                    break

            copy_assignment.remove_assignment(xj)

            if not consistent_extension_found:
                info.store_domain_for(xi, csp.get_domain(xi))
                csp.remove_value_from_domain(xi, i_value)
                revised = True

        return revised

# Possible heuristics of variables selection in ImprovedBacktrackingStrategy
class Selection:
    DEFAULT_ORDER = 0
    MRV = 1
    MRV_DEG = 2

# Inference strategies in ImprovedBacktrackingStrategy
class Inference:
    NONE = 0
    FORWARD_CHECKING = 1
    AC3 = 2

class ImprovedBacktrackingStrategy(BacktrackingStrategy):
    def __init__(self, selection, inference=Inference.NONE, enable_lcv=False):
        super().__init__()
        self.selection = selection
        self.inference = inference
        self.enable_lcv = enable_lcv

    def solve(self, csp):
        if self.inference == Inference.AC3:
            info = AC3Strategy().reduce_domains(csp)

            if not info.is_empty():
                self._notify_state_changed(csp)
                if info.empty_domain_found:
                    return None

        return super().solve(csp)

    def _select_unassigned_variable(self, assignment, csp):
        if self.selection == Selection.MRV:
            return self._apply_mrv_heuristic(csp, assignment)[0]
        elif self.selection == Selection.MRV_DEG:
            vars = self._apply_mrv_heuristic(csp, assignment)
            return self._apply_degree_heuristic(vars, assignment, csp)[0]
        else:
            return super()._select_unassigned_variable(assignment, csp)

    def _apply_mrv_heuristic(self, csp, assignment):
        """
        Return list of variables with the least number of assignable variables

        :param csp (CSP): CSP to solve
        :param assignment (Assignment): current assignment
        :return list(Variable): list of variales with the least number of assignable variables
        """
        result = []
        mrv = PlusInfinity()
        copy_assignment = assignment.copy()

        for var in csp.get_variables():
            if not copy_assignment.has_assignment_for(var):
                # Get number of left values for this variable
                num = self._calculate_left_values(var, csp, copy_assignment)
                if num <= mrv:
                    if num < mrv:
                        result = []
                        mrv = num
                    result.append(var)

        return result

    def _calculate_left_values(self, var, csp, assignment):
        num = 0

        for val in csp.get_domain(var):
            # Set value
            assignment.set_assignment(var, val)
            violated = False
            # Check if any constraint is violated
            for constraint in csp.get_constraints(var):
                if not constraint.is_satisfied_with(assignment):
                    violated = True
            # If not violated this value can be set
            if not violated:
                num += 1

            assignment.remove_assignment(var)

        return num


    def _apply_degree_heuristic(self, vars, assignment, csp):
        """
        Find variable with the biggest degree

        :param vars list(Variable): list of variables with the least number of assignable values
        :param assignment (Assignment): current assignment
        :param csp (CSP): CSP to solve
        :return: result list of variables with the highest degree. Result variables is subset of vars.
        """

        result = []
        max_degree = -1

        for var in vars:
            neighbors = set()
            for constraint in csp.get_constraints(var):
                for neighbor in constraint.get_scope():
                    # Collect all not assigned variables with common constraints
                    if not assignment.has_assignment_for(neighbor):
                        neighbors.add(neighbor)

            # Number of collected variables is a degree of the current variable
            degree = len(neighbors)
            if degree >= max_degree:
                if degree > max_degree:
                    result = []
                    max_degree = degree
                result.append(var)

        return result

    def _order_domain_values(self, var, csp, assignment):
        if self.enable_lcv:
            return self._apply_least_constraining_value_heuristic(var, csp, assignment)
        else:
            return super()._order_domain_values(var, csp, assignment)

    def _apply_least_constraining_value_heuristic(self, var, csp, assignment):
        pairs = []
        for value in csp.get_domain(var):
            num = self._count_lost_values(var, value, csp, assignment)
            pairs.append((value, num))

        pairs = sorted(pairs, key = lambda pair: pair[1])

        return [value for (value, num) in pairs]

    def _count_lost_values(self, var, value, csp, assignment):
        copy_assignment = assignment.copy()
        assignment.set_assignment(var, value)

        result = 0
        for constraint in csp.get_constraints():
            for neighbor in constraint.get_scope():
                if neighbor != var:
                    for n_value in csp.get_domain(neighbor):
                        copy_assignment.set_assignment(neighbor, n_value)
                        if not constraint.is_satisfied_with(copy_assignment):
                            result += 1
                    copy_assignment.remove_assignment(neighbor)
                
        return result

    def _inference(self, var, assignment, csp):
        if self.inference == Inference.FORWARD_CHECKING:
            return self._do_forward_checking(var, assignment, csp)
        elif self.inference == Inference.AC3:
            return AC3Strategy().reduce_domains(csp, var, assignment.get_assignment(var), assignment)
        else:
            return super()._inference(var, assignment, csp)


    def _do_forward_checking(self, var, assignment, csp):
        result = DomainRestoreInfo()

        for constraint in csp.get_constraints(var):
            for neighbor in constraint.get_scope():
                if not assignment.has_assignment_for(neighbor):
                    if self._revise(neighbor, constraint, assignment, csp, result):
                        if csp.get_domain(neighbor).is_empty():
                            result.empty_domain_found = True
                            return result

        return result

    def _revise(self, var, constraint, assignment, csp, info):
        revised = False

        for value in csp.get_domain(var):
            assignment.set_assignment(var, value)
            if not constraint.is_satisfied_with(assignment):
                info.store_domain_for(var, value)
                revised = True

            assignment.remove_assignment(var)

        return  revised

# Artificial Intelligence A Modern Approach (3rd Ed.): Figure 6.8, Page 221.
#
# function MIN-CONFLICTS(csp, max-steps) returns a solution or failure
#    inputs: csp, a constraint satisfaction problem
#            max-steps, the number of steps allowed before giving up
#    current = an initial complete assignment for csp
#    for i = 1 to max steps do
#       if current is a solution for csp then return current
#       var = a randomly chosen conflicted variable from csp.VARIABLES
#       value = the value v for var that minimizes CONFLICTS(var, v, current, csp)
#       set var = value in current
#    return failure
# 
# Figure 6.8 The MIN-CONFLICTS algorithm for solving CSPs by local search. The
# initial state may be chosen randomly or by a greedy assignment process that
# chooses a minimal-conflict value for each variable in turn. The CONFLICTS
# function counts the number of constraints violated by a particular value,
# given the rest of the current assignment.
class MinConflictsStrategy(SolutionStrategy):
    def __init__(self, max_step):
        super().__init__()
        self.max_step = max_step

    # function MIN-CONFLICTS(csp, max-steps) returns a solution or failure
    def solve(self, csp):
        # current = an initial complete assignment for csp
        assignment = self._generate_random_assignment(csp)
        self._notify_state_changed(csp)
        # for i = 1 to max steps do
        for i in range(self.max_step):
            # if current is a solution for csp then return current
            if assignment.is_solution(csp):
                return assignment
            else:
                # var = a randomly chosen conflicted variable from csp.VARIABLES
                vars = self._get_conflicted_variables(assignment, csp)
                var = select_randomly_from_list(vars)
                # value = the value v for var that minimizes CONFLICTS(var, v, current, csp)
                value = self._get_min_conflict_value_for(var, assignment, csp)
                # set var = value in current
                assignment.set_assignment(var, value)
                self._notify_state_changed(csp, assignment)

        # return failure
        return None

    def _generate_random_assignment(self, csp):
        assignment = Assignment()
        for var in csp.get_variables():
            value = select_randomly_from_list(list(csp.get_domain(var)))
            assignment.set_assignment(var, value)

        return assignment

    def _get_conflicted_variables(self, assignment, csp):
        result = set()
        for constraint in csp.get_constraints():
            if not constraint.is_satisfied_with(assignment):
                for var in constraint.get_scope():
                    result.add(var)

        return list(result)

    def _get_min_conflict_value_for(self, var, assignment, csp):
        constraints = csp.get_constraints()
        duplicate_assignment = assignment.copy()
        min_conflict = PlusInfinity()
        result_candidates = []

        for value in csp.get_domain(var):
            duplicate_assignment.set_assignment(var, value)
            curr_conflict = self._count_conflicts(assignment, constraints)
            if curr_conflict <= min_conflict:
                if curr_conflict < min_conflict:
                    result_candidates = []
                    min_conflict = curr_conflict
                result_candidates.append(value)

        if len(result_candidates) != 0:
            return select_randomly_from_list(result_candidates)
        else:
            return None

    def _count_conflicts(self, assignment, constraints):
        result = 0
        for constraint in constraints:
            if not constraint.is_satisfied_with(assignment):
                result += 1

        return result
            

class MapCSP(CSP):
    NSW = Variable("NSW")
    NT = Variable("NT")
    Q = Variable("Q")
    SA = Variable("SA")
    T = Variable("T")
    V = Variable("V")
    WA = Variable("WA")
    RED = "RED"
    GREEN = "GREEN"
    BLUE = "BLUE"

    def __init__(self):
        super().__init__(self._collect_variables())
        colors = Domain((self.RED, self.GREEN, self.BLUE))

        for var in self.get_variables():
            self.set_domain(var, colors)

        self.add_constraint(NotEqualConstraint(self.WA, self.NT))
        self.add_constraint(NotEqualConstraint(self.WA, self.SA))
        self.add_constraint(NotEqualConstraint(self.NT, self.SA))
        self.add_constraint(NotEqualConstraint(self.NT, self.Q))
        self.add_constraint(NotEqualConstraint(self.SA, self.Q))
        self.add_constraint(NotEqualConstraint(self.SA, self.NSW))
        self.add_constraint(NotEqualConstraint(self.SA, self.V))
        self.add_constraint(NotEqualConstraint(self.Q, self.NSW))
        self.add_constraint(NotEqualConstraint(self.NSW, self.V))

    def _collect_variables(self):
        variables = []
        variables.append(self.NSW)
        variables.append(self.NT)
        variables.append(self.Q)
        variables.append(self.SA)
        variables.append(self.T)
        variables.append(self.V)
        variables.append(self.WA)

        return variables
