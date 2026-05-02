# abstract_math

## Description
The abstract_math Python module, currently in its Alpha development stage (version 0.0.0.14), is designed for performing complex mathematical operations and token manipulations. This module comprises primarily of two scripts: `safe_math` and `derive_tokens`.

## Features
- Performing complex mathematical operations.
- Manipulation and derivation of mathematical tokens, referred to as 'lamports'.
- High precision for decimal calculations for better accuracy.
- Functions for deriving quantities like lamports, virtual reserves, sol reserves, sol amounts, token reserves, token amounts, derived token ratio, price, and token decimals.
- Module components for updating Sol and token variables.

### Module Overview: `adapt_units_api.py`
This module serves as the primary physics engine and unit-translation layer for simulating 1D radial trajectories (straight up/down flight) and calculating planetary surface visibility. It handles the orchestration between arbitrary user input units, the core SI-based forward-Euler integrator, and the final output formatting.

---

### Function Reference

#### `normalize_inputs`
**Description:** Acts as the input sanitization layer. It takes human-readable inputs with arbitrary distance and time units and converts them into strict SI units (meters, seconds, meters/second). Crucially, it also uses the `flight_path_angle_deg` to extract the purely radial (vertical) component of the starting velocity, ignoring lateral motion.

**Parameters:**
* `planet` (*str*): The identifier for the celestial body being simulated.
* `start_altitude` (*float*): The initial altitude above the planet's surface.
* `starting_velocity` (*float*): The total initial velocity vector magnitude.
* `input_dist_unit` (*str*): The unit string for input distances (e.g., 'km', 'mi').
* `input_time_unit` (*str*): The unit string for input times (e.g., 's', 'hr').
* `target_distance` (*float*, optional): The desired target altitude to reach.
* `flight_path_angle_deg` (*float*, default: 90.0): The angle of the velocity vector relative to the local horizon (90° = straight up).

**Returns:** * *dict*: A dictionary containing normalized SI values (`start_alt_m`, `target_alt_m`, `v0_mps` [radial velocity], `total_v0_mps`, and `flight_path_angle_deg`).

---

#### `analyze_visible_surface`
**Description:** A diagnostic utility that generates a scan of visible surface areas from a planet at incrementally increasing altitudes and different camera Fields of View (FOV). It calculates the spherical cap area visible to an observer and converts the mathematical outputs (in meters) directly into the requested display units. It does not return data to the integrator; it is purely for analysis and reporting.

**Parameters:**
* `altitude_step` (*float*): The increment added to the altitude for each step in the scan.
* `max_steps` (*int*): The total number of altitude increments to calculate.
* `fov_range` (*tuple[int, int]*): The min and max Field of View angles in degrees.
* `fov_interval` (*int*): The step size between FOV calculations.
* `input_dist_unit` (*str*): The unit system used to interpret the `altitude_step`.
* `display_units` (*str*): The unit system used for printing output areas and radii.
* `planet` (*str*): The celestial body being observed.
* `printit` (*bool*): If True, prints the generated scan to the console.

**Returns:**
* *dict*: A structured dictionary (`all_stats`) containing the raw text output, units used, and a nested list of variables calculated at every altitude/FOV combination.

---

#### `calculate_avrt`
**Description:** The core physics step function. It performs a single iteration of a Forward-Euler numerical integration to update the kinematic state of an object in a radial gravity field. It calculates local gravitational acceleration using the formula $a = -\frac{\mu}{r^2}$.

**Parameters:**
* `mu` (*float*): The standard gravitational parameter of the planet ($GM$).
* `v` (*float*): Current radial velocity in m/s.
* `r` (*float*): Current distance from the planet's center in meters.
* `t` (*float*): Current simulation time in seconds.
* `dt_s` (*float*): The time-step delta in seconds.
* `steps` (*int*): The current iteration count.

**Returns:**
* *tuple*: The updated kinematic state `(v, r, t, steps)`.

---

#### `init_tracker`
**Description:** A lightweight helper function that initializes the state dictionary used to track maximums and totals during the simulation loop.

**Parameters:**
* `r0` (*float*): The initial radius from the center of the planet.

**Returns:**
* *dict*: A tracking dictionary with default values for apoapsis tracking (`furthest_r`, `time_at_furthest`, etc.).

---

#### `simulate_radial_flight_si`
**Description:** The main simulation loop. It repeatedly calls `calculate_avrt` to advance the object's state through time using strict SI units. The loop monitors for specific exit conditions: hitting the planet's surface, reaching a predefined target altitude, or turning back (reaching apoapsis and falling).

**Parameters:**
* `v0_mps` (*float*): Initial radial velocity in m/s.
* `start_alt_m` (*float*): Initial altitude above the surface in meters.
* `planet` (*str*): The celestial body dictating the gravity field.
* `dt_s` (*float*, default: 1.0): The integration time-step.
* `max_steps` (*int*): The maximum allowed loop iterations before timing out.
* `target_alt_m` (*float*, optional): The altitude that triggers a successful "hit_target" exit.

**Returns:**
* *dict*: The final simulation state, including boolean flags for how the simulation ended (`hit_surface`, `hit_target`, `turned_back`), final kinematics, local gravity data, and extended tracking stats (like max altitude reached).

---

#### `radial_travel`
**Description:** The primary public-facing wrapper API. It orchestrates the entire lifecycle of a simulation request. It uses `normalize_inputs` to sanitize the user data, feeds it into `simulate_radial_flight_si`, and finally converts all output data from SI meters/seconds back into the user's specified `output_dist_unit` and `output_time_unit`.

**Parameters:**
* `starting_velocity` (*float*): Initial velocity magnitude.
* `start_altitude` (*float*): Initial altitude above the surface.
* `input_dist_unit` (*str*): Units for input distance/altitude.
* `input_time_unit` (*str*): Units for input time.
* `output_dist_unit` (*str*): Desired units for the returned distances/altitudes.
* `output_time_unit` (*str*): Desired units for the returned time/velocities.
* `planet` (*str*): Target celestial body.
* `dt_s` (*float*): Simulation time-step resolution.
* `max_steps` (*int*): Simulation iteration limit.
* `target_distance` (*float*, optional): Goal altitude to trigger simulation halt.
* `flight_path_angle_deg` (*float*, default: 90.0): Launch angle.

**Returns:**
* *dict*: A highly detailed dictionary containing a recap of the inputs, the final converted kinematic state (altitude, velocity, time), completion flags, gravity metrics, and apoapsis (furthest distance) statistics. Returns an error dict if the simulation fails to initialize.