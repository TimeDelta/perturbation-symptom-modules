"""Numerical checks for the fixed-point-against-relaxation-rate report.

Toy signed network with heterogeneous relaxation rates. Node classes:
  0 drug target protein activity (fast), 1 metabolite (fast), 2 reaction node (algebraic, very fast),
  3 metabolite produced and consumed (two-sign destination), 4 transcript (slow), 5 protein abundance (very slow),
  6 membrane-potential-like node (very fast).
"""
import numpy as np

rng = np.random.default_rng(0)

number_of_nodes = 7
# dimensionless per-relaxation-time gains (what the encoder's gain_r * S_r represent); rows = destination
dimensionless_gain_matrix = np.zeros((number_of_nodes, number_of_nodes))
dimensionless_gain_matrix[2, 0] = 0.6      # protein activity -> reaction flux
dimensionless_gain_matrix[1, 2] = 0.5      # reaction -> product metabolite (product_of, +)
dimensionless_gain_matrix[3, 2] = 0.45     # reaction -> two-sign metabolite, production (+)
dimensionless_gain_matrix[3, 1] = -0.45    # metabolite 1 drives a consuming reaction of node 3 (depletion, -)
dimensionless_gain_matrix[4, 1] = 0.4      # metabolite -> transcription of a gene (slow process edge)
dimensionless_gain_matrix[5, 4] = 0.8      # transcript -> protein abundance (encodes, slow process edge)
dimensionless_gain_matrix[0, 5] = 0.3      # protein abundance feeds back on activity node (abundance x specific activity)
dimensionless_gain_matrix[6, 1] = 0.5      # metabolite -> membrane potential-like node
dimensionless_gain_matrix[6, 5] = -0.2     # protein abundance -> membrane node
assert np.max(np.abs(dimensionless_gain_matrix).sum(axis=1)) < 1.0, "row sums must stay below one for the contraction"

sustained_input = np.zeros(number_of_nodes)
sustained_input[0] = -1.0  # drug blocks the target's activity

identity = np.eye(number_of_nodes)
full_fixed_point = np.linalg.solve(identity - dimensionless_gain_matrix, sustained_input)

# relaxation rates per node in 1/hour: activity (s), metabolite (min), reaction (algebraic ~ instantaneous),
# two-sign metabolite (min), transcript (9 h half-life), protein abundance (9 d lifetime), membrane node (ms)
relaxation_rate_per_hour = np.array([3600.0, 60.0, 1e5, 60.0, np.log(2) / 9.0, 1.0 / (9.0 * 24.0), 3.6e6])

def damped_iteration_fixed_point(step_sizes_per_node, max_rounds=200000, tolerance=1e-12):
    """h(t+1) = h(t) + d_i (-h_i(t) + sum_j G_ij h_j(t) + u_i), with a per-node step d_i in (0, 1]."""
    state = sustained_input.copy()
    for _ in range(max_rounds):
        next_state = state + step_sizes_per_node * (-state + dimensionless_gain_matrix @ state + sustained_input)
        if np.max(np.abs(next_state - state)) < tolerance:
            return next_state
        state = next_state
    return state

# 1. Fixed point invariance to the rates when the dimensionless gains are held fixed
uniform_step = damped_iteration_fixed_point(np.full(number_of_nodes, 0.5))
physical_time_step_hours = 1e-7  # must be small enough for the fastest node: d_i = kappa_i * dt <= 1
heterogeneous_step = damped_iteration_fixed_point(np.minimum(relaxation_rate_per_hour * physical_time_step_hours * 1e6, 0.9))
print("1. fixed point with uniform damping   :", np.round(uniform_step, 6))
print("   fixed point with per-node step d_i :", np.round(heterogeneous_step, 6))
print("   max abs difference                 :", np.max(np.abs(uniform_step - heterogeneous_step)))

# 2. What changes if the ABSOLUTE coupling rates are held fixed and D is rescaled
absolute_coupling_matrix = np.diag(relaxation_rate_per_hour) @ dimensionless_gain_matrix  # A = D * G
absolute_input = relaxation_rate_per_hour * sustained_input                            # u = D * u_tilde
for scale_factor in (1.0, 2.0, 10.0):
    scaled_rates = scale_factor * relaxation_rate_per_hour
    fixed_point_scaled_rates = np.linalg.solve(np.diag(scaled_rates) - absolute_coupling_matrix, absolute_input)
    print(f"2. D scaled by {scale_factor:>4}: fixed point", np.round(fixed_point_scaled_rates, 6))

# 3. Quasi-steady-state (acute) equilibrium: slow processes frozen. Slow edges: metabolite->transcript (4,1),
#    transcript->protein abundance (5,4). Freezing them is the same as clamping nodes 4 and 5 at zero here,
#    because those nodes have no fast in-edges.
slow_edge_mask = np.zeros_like(dimensionless_gain_matrix, dtype=bool)
slow_edge_mask[4, 1] = True
slow_edge_mask[5, 4] = True
fast_operator = dimensionless_gain_matrix.copy()
fast_operator[slow_edge_mask] = 0.0
acute_fixed_point = np.linalg.solve(identity - fast_operator, sustained_input)
print("3. acute (slow edges frozen) fixed point:", np.round(acute_fixed_point, 6))
print("   full fixed point                      :", np.round(full_fixed_point, 6))

# Tikhonov check: integrate the true heterogeneous-rate system and read it at 1 hour, 1 day, 100 days
def integrate_continuous(read_times_hours):
    jacobian = np.diag(relaxation_rate_per_hour) @ (dimensionless_gain_matrix - identity)
    forcing = relaxation_rate_per_hour * sustained_input
    readings = {}
    # closed form for a linear system: h(t) = J^-1 (expm(J t) - I) f ; use eigen-decomposition
    eigenvalues, eigenvectors = np.linalg.eig(jacobian)
    inverse_eigenvectors = np.linalg.inv(eigenvectors)
    for read_time in read_times_hours:
        propagator = eigenvectors @ np.diag((np.exp(eigenvalues * read_time) - 1.0) / eigenvalues) @ inverse_eigenvectors
        readings[read_time] = np.real(propagator @ forcing)
    return readings

for read_time, reading in integrate_continuous([1.0, 24.0, 24.0 * 100]).items():
    print(f"   true state at t = {read_time:>7.1f} h:", np.round(reading, 6))

# Schur complement identity: the reduced slow system's fixed point equals the full fixed point
fast_nodes = [0, 1, 2, 3, 6]
slow_nodes = [4, 5]
G_ff = dimensionless_gain_matrix[np.ix_(fast_nodes, fast_nodes)]
G_fs = dimensionless_gain_matrix[np.ix_(fast_nodes, slow_nodes)]
G_sf = dimensionless_gain_matrix[np.ix_(slow_nodes, fast_nodes)]
G_ss = dimensionless_gain_matrix[np.ix_(slow_nodes, slow_nodes)]
inverse_fast = np.linalg.inv(np.eye(len(fast_nodes)) - G_ff)
reduced_slow_operator = G_ss + G_sf @ inverse_fast @ G_fs
reduced_slow_input = sustained_input[slow_nodes] + G_sf @ inverse_fast @ sustained_input[fast_nodes]
slow_fixed_point_reduced = np.linalg.solve(np.eye(len(slow_nodes)) - reduced_slow_operator, reduced_slow_input)
print("   Schur-reduced slow fixed point:", np.round(slow_fixed_point_reduced, 6), " full:", np.round(full_fixed_point[slow_nodes], 6))

# 4. Frequency response: once-daily dosing, first harmonic, per-node attenuation relative to DC
dosing_period_hours = 24.0
fundamental_angular_frequency = 2 * np.pi / dosing_period_hours
for harmonic_index in (1, 2):
    shifted_operator = identity - dimensionless_gain_matrix + 1j * harmonic_index * fundamental_angular_frequency * np.diag(1.0 / relaxation_rate_per_hour)
    harmonic_response = np.linalg.solve(shifted_operator, sustained_input.astype(complex))
    ratio_to_dc = np.abs(harmonic_response) / np.maximum(np.abs(full_fixed_point), 1e-15)
    print(f"4. harmonic {harmonic_index}: |response| / |DC response| per node:", np.round(ratio_to_dc, 4))

# 5. Fourier content of the exponential concentration sawtooth for several half-lives, once daily
for half_life_hours, drug_name in ((7.0, "quetiapine-like"), (36.0, "citalopram-like"), (96.0, "fluoxetine-like, parent"), (11 * 24.0, "norfluoxetine-like")):
    elimination_rate = np.log(2) / half_life_hours
    first_harmonic_over_mean = 1.0 / np.sqrt(1.0 + (fundamental_angular_frequency / elimination_rate) ** 2)
    peak_over_mean = elimination_rate * dosing_period_hours / (1.0 - np.exp(-elimination_rate * dosing_period_hours))
    trough_over_mean = peak_over_mean * np.exp(-elimination_rate * dosing_period_hours)
    print(f"5. {drug_name:28s} t_half {half_life_hours:5.0f} h: |c_1|/c_mean = {first_harmonic_over_mean:.3f}, "
          f"peak/mean = {peak_over_mean:.2f}, trough/mean = {trough_over_mean:.2f}, peak/trough = {peak_over_mean / trough_over_mean:.1f}")

# 6. Time to pharmacokinetic steady state in half-lives
for number_of_half_lives in (3.3, 5.0, 7.0):
    print(f"6. after {number_of_half_lives} half-lives the accumulation reaches {1 - 2 ** (-number_of_half_lives):.3f} of steady state")

# 7. The exact two-sign cancellation under row scaling: row 3 receives +0.45 from the reaction and -0.45 from metabolite 1.
row_three_gain_sum = dimensionless_gain_matrix[3].sum()
print("7. two-sign row sum before scaling:", row_three_gain_sum, " after dividing the row by its rate:", row_three_gain_sum / relaxation_rate_per_hour[3])
