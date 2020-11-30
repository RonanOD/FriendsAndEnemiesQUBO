# From Joel Gottlieb - Tut- 2 https://www.youtube.com/watch?v=vknIOydOJOo&ab_channel=D-WaveSystems
import dimod

exactsolver = dimod.ExactSolver()

# Prob 3 - Set A = {1,2,3,4,5}; Find 3 numbers in A that add up to 8?

Q = {('a1', 1): 1, ('a2', 1): 2, ('a3', 1): 3, ('a4', 1): 4, ('a5', 1): 5}

bqm = dimod.BinaryQuadraticModel.from_qubo(Q)
results = exactsolver.sample(bqm)

# Print everything out
for sample, energy in results.data(['sample', 'energy']):
    print(sample, energy)