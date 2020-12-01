# From Joel Gottlieb - Tut- 2 https://www.youtube.com/watch?v=vknIOydOJOo&ab_channel=D-WaveSystems
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite

# Taken from https://www.dwavesys.com/sites/default/files/3_Seminar_Victoria.pdf
# Prob 3 - Set A = {1,2,3,4,5}; Find 3 numbers in A that add up to 8?
sampler = EmbeddingComposite(DWaveSampler())
# Define Q
Q = {(1,1): -1, (1,2): 1, (1,3): 1,
     (2,2): -1, (2,4): 1,
     (3,3): -1, (3,4): 1,
     (4,4): -1}

response = sampler.sample_qubo(Q)

print(response)


"""
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

"""
