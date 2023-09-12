from utils import first


# Variable ordering

def first_unassigned_variable(assignment, csp):
    """The default variable order."""
    return first([var for var in csp.variables if var not in assignment])


def cnt_values(csp, var, assignment):
    if csp.curr_domains:
        return len(csp.curr_domains[var])
    else:
        cnt = 0
        for val in csp.domains[var]:
            if csp.nconflicts(var, val, assignment) == 0:
                cnt += 1
    return cnt


def mrv(assignment, csp):
    twmp = None
    mini = 1e9
    for x in csp.variables:
        if x not in assignment.keys():
            if cnt_values(csp, x, assignment) < mini:
                temp = x
                mini = cnt_values(csp, x, assignment)
    return temp


# Value ordering

def unordered_domain_values(var, assignment, csp):
    """The default value order."""
    return csp.choices(var)


def lcv(var, assignment, csp):
    return sorted(csp.choices(var), key=lambda val: csp.nconflicts(var, val, assignment))


# Filtering

def no_inference(csp, var, value, assignment, removals):
    return True


def forward_checking(csp, var, value, assignment, removals):
    for x in csp.neighbors[var]:
        if x not in assignment:
            for d in csp.curr_domains[x][:]:
                if not csp.constraints(var, value, x, d):
                    csp.prune(x, d, removals)
            if not csp.curr_domains[x]:
                return False
    return True


def arc_cons(csp, var, value, assignment, removals):
    csp.support_pruning()
    queue = [(n, var) for n in csp.neighbors[var]]

    while queue:
        (a, b) = queue.pop()
        flag = False
        for x in csp.curr_domains[a][:]:
            if all(not csp.constraints(a, x, b, y) for y in csp.curr_domains[b]):
                csp.prune(a, x, removals)
                flag = True
        if flag:
            if not csp.curr_domains[a]:
                return False
            for z in csp.neighbors[a]:
                if z != a:
                    queue.append((z, a))
    return True


def backtracking_search(csp,
                        select_unassigned_variable=first_unassigned_variable,
                        order_domain_values=unordered_domain_values,
                        inference=forward_checking):
    def backtrack(assignment):
        if len(assignment) == len(csp.variables):
            return assignment
        var = select_unassigned_variable(assignment, csp)
        for value in order_domain_values(var, assignment, csp):
            if 0 == csp.nconflicts(var, value, assignment):
                csp.assign(var, value, assignment)
                removals = csp.suppose(var, value)
                if inference(csp, var, value, assignment, removals):
                    result = backtrack(assignment)
                    if result is not None:
                        return result
                csp.restore(removals)
        csp.unassign(var, assignment)
        return None

    result = backtrack({})
    assert result is None or csp.goal_test(result)
    return result
