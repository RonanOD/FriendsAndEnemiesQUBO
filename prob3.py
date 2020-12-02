# From Joel Gottlieb - Tut- 2 Prob 3 - https://www.youtube.com/watch?v=vknIOydOJOo&ab_channel=D-WaveSystems

# Solution code hugely influenced from D-Wave knapsack example: https://github.com/RonanOD/knapsack

import pandas as pd
import sys
from dwave.system import LeapHybridSampler
from math import log2, floor
import dimod

def build_bqm(costs, weights, weight_capacity):
    """Construct BQM
    
    Args:
        costs (array-like):
            Array of costs associated with the items
        weights (array-like):
            Array of weights associated with the items
        weight_capacity (int):
            Maximum allowable weight
    
    Returns:
        Binary quadratic model instance
    """

    # Initialize BQM - use large-capacity BQM so that the problem can be
    # scaled by the user.
    bqm = dimod.AdjVectorBQM(dimod.Vartype.BINARY)

    # Lagrangian multiplier
    # First guess as suggested in Lucas's paper
    lagrange = max(costs)

    # Number of objects
    x_size = len(costs)

    # Lucas's algorithm introduces additional slack variables to
    # handle the inequality. M+1 binary slack variables are needed to
    # represent the sum using a set of powers of 2.
    M = floor(log2(weight_capacity))
    num_slack_variables = M + 1

    # Slack variable list for Lucas's algorithm. The last variable has
    # a special value because it terminates the sequence.
    y = [2**n for n in range(M)]
    y.append(weight_capacity + 1 - 2**M)

    # Hamiltonian xi-xi terms
    for k in range(x_size):
        bqm.set_linear('x' + str(k), lagrange * (weights[k]**2) - costs[k])

    # Hamiltonian xi-xj terms
    for i in range(x_size):
        for j in range(i + 1, x_size):
            key = ('x' + str(i), 'x' + str(j))
            bqm.quadratic[key] = 2 * lagrange * weights[i] * weights[j]

    # Hamiltonian y-y terms
    for k in range(num_slack_variables):
        bqm.set_linear('y' + str(k), lagrange * (y[k]**2))

    # Hamiltonian yi-yj terms
    for i in range(num_slack_variables):
        for j in range(i + 1, num_slack_variables):
            key = ('y' + str(i), 'y' + str(j))
            bqm.quadratic[key] = 2 * lagrange * y[i] * y[j]

    # Hamiltonian x-y terms
    for i in range(x_size):
        for j in range(num_slack_variables):
            key = ('x' + str(i), 'y' + str(j))
            bqm.quadratic[key] = -2 * lagrange * weights[i] * y[j]

    return bqm

def solve(costs, weights, weight_capacity, sampler=None):
    """Construct BQM and solve the problem
    
    Args:
        costs (array-like):
            Array of costs associated with the items
        weights (array-like):
            Array of weights associated with the items
        weight_capacity (int):
            Maximum allowable weight
        sampler (BQM sampler instance or None):
            A BQM sampler instance or None, in which case
            LeapHybridSampler is used by default
    
    Returns:
        Tuple:
            List of indices of selected items
            Solution energy
    """
    bqm = build_bqm(costs, weights, weight_capacity)

    if sampler is None:
        sampler = LeapHybridSampler()

    sampleset = sampler.sample(bqm)
    sample = sampleset.first.sample
    energy = sampleset.first.energy

    # Build solution from returned binary variables:
    selected_item_indices = []
    for varname, value in sample.items():
        # For each "x" variable, check whether its value is set, which
        # indicates that the corresponding item is included in the
        # knapsack
        if value and varname.startswith('x'):
            # The index into the weight array is retrieved from the
            # variable name
            selected_item_indices.append(int(varname[1:]))

    return sorted(selected_item_indices), energy


if __name__ == '__main__':
    # Weight capacity is what we want only 3 of the 5 numbers to add to:
    weight_capacity = 8
    # Construct a dict that is the set of {1,2,3,4,5}
    d = {'cost': [1, 2, 3, 4, 5], 'weight': [1, 2, 3, 4, 5]}
    df = pd.DataFrame(data=d)

    selected_item_indices, energy = solve(df['cost'], df['weight'], weight_capacity)
    selected_weights = list(df.loc[selected_item_indices,'weight'])
    selected_costs = list(df.loc[selected_item_indices,'cost'])

    print("Found solution at energy {}".format(energy))
    print("Selected item numbers (0-indexed):", selected_item_indices)
    print("Selected item weights: {}, total = {}".format(selected_weights, sum(selected_weights)))
    print("Selected item costs: {}, total = {}".format(selected_costs, sum(selected_costs)))

"""
NOTES:

My first solution:

Q = {('a1', 1): 1, ('a2', 1): 2, ('a3', 1): 3, ('a4', 1): 4, ('a5', 1): 5}

bqm = dimod.BinaryQuadraticModel.from_qubo(Q)
results = exactsolver.sample(bqm)

# Print everything out
for sample, energy in results.data(['sample', 'energy']):
    print(sample, energy)
"""

"""
From Joel:
 I write the “add up to 8” equation in the following way:
 x_1 + 2x_2 + 3x_3 + 4x_4 + 5x_5 = 8

 and then the “need to use three numbers” equation is this:
 x_1 + x_2 + x_3 + x_4 + x_5 = 3

I replied:

That makes a lot more sense to me. So to make this QUBO appropriate you take the two formulas:

objective => x1 + 2x_2 + 3x_3 + 4x_4 + 5x_5 = 8
constraints => x_1 + x_2 + x_3 + x_4 + x_5 = 3

and join them together as:

min( x1 + 2x_2 + 3x_3 + 4x_4 + 5x_5 - 8) + GAMMA((  x_1 + x_2 + x_3 + x_4 + x_5 -3) ** 2)

From Joel:
Ronan,

The equation is slightly different:

min(( x1 + 2x_2 + 3x_3 + 4x_4 + 5x_5 - 8) ** 2) + GAMMA((  x_1 + x_2 + x_3 + x_4 + x_5 -3) ** 2)

Both expressions need to be squared.

"""
