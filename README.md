# Hash Code Archive — Photo Slideshow Optimization

This project implements heuristic and local search algorithms to solve the **Google Hash Code 2019 “Photo Slideshow” challenge**. The goal is to arrange a set of photos into a slideshow that maximizes the total interest score between consecutive slides.

The project combines data preprocessing, heuristic construction, and iterative optimization, making it suitable as a thorough case study in heuristic and local search methods.

---

## Problem Description

Each photo is described by:
- orientation (`H` – horizontal, `V` – vertical),
- a set of textual tags.

A **slide** consists of:
- one horizontal photo, or
- a pair of vertical photos.

The interest score between two slides `A` and `B` is defined as:

```markdown
\[
\text{score}(A, B) = \min \Big(
\lvert \text{tags}(A) \cap \text{tags}(B) \rvert,\;
\lvert \text{tags}(A) \setminus \text{tags}(B) \rvert,\;
\lvert \text{tags}(B) \setminus \text{tags}(A) \rvert
\Big)
\]
```


The objective is to **maximize the sum of scores over all consecutive slide pairs** in the slideshow.

---

## Implemented Features

### 1. Data Preprocessing
- Efficient loading of JSON data
- Separation of horizontal and vertical photos
- Tag representation using Python sets

### 2. Vertical Photo Pairing
Implemented strategies:
- `random` – random pairing
- `similar` – maximize tag overlap
- `different` – minimize tag overlap (diversification)

### 3. Slide Ordering Heuristics
- **Random**
- **Nearest Neighbor (NN)** – greedy local selection
- **Grouped** – grouping slides by representative tag
- **Mixed** – grouping + NN inside and between groups

### 4. Local Optimization (Core Optimization Part)
- **Swap-based hill climbing**
- **2-opt neighborhood search**
- **Simulated annealing**
- Delta-based score evaluation for efficiency

These methods iteratively improve an initial heuristic solution and form the core optimization component of the project.

---

## Running the Solver (CLI)

Example command:

```bash
python3 solver.py \
    --data_dir ../data \
    --out submission.txt \
    --seed 42 \
    --pairing different \
    --order mixed \
    --k 300 \
    --k_group 10 \
    --group_key first \
    --local_iters 1000 \
    --eval
```

--- 

## Optimization Strategy

The optimization pipeline follows a multi-stage approach:

### Heuristic construction  
Fast generation of a reasonably good initial solution using greedy and grouped heuristics.

### Iterative local improvement  
Repeated neighborhood exploration using **swap** and **2-opt** moves to improve the total slideshow score.

### Stochastic escape mechanisms  
**Simulated annealing** is applied to probabilistically accept worse moves, allowing the algorithm to escape local optima.

### Multi-start strategy  
The solver is executed multiple times with different random seeds, and the best solution is retained.

This approach balances **exploration** (randomness and stochastic moves) and **exploitation** (greedy improvement), while keeping runtime manageable.

---

## Experimental Analysis

The project includes extensive empirical evaluation, covering:

- comparison of different ordering heuristics,
- sensitivity analysis of parameters (`k`, `k_group`, number of iterations),
- trade-offs between runtime and solution quality,
- evaluation of vertical photo pairing strategies,
- convergence plots illustrating the behavior of local search methods.

Results, plots, and experiments can be found in:

- `reports/`
- `notebooks/`
- LaTeX documentation located in `documentation/`

---

## Key Observations

- Pure greedy heuristics quickly stagnate in poor local optima.
- Local optimization significantly improves solution quality over heuristic-only approaches.
- The method of pairing vertical photos has a strong impact on the final slideshow score.
- Introducing randomness is essential for escaping local optima.
- The best results are obtained using a **mixed heuristic combined with local search**.

---

## References

- Google Hash Code 2019 – *Photo Slideshow* problem statement  
- Standard literature on local search and combinatorial optimization

---

## License

This project is released under the **MIT License**.

---

## Authors

Developed by **Alesia Filinkova**  and **Sofiya Yedzeika**
as part of the *Foundations of Optimization* course project.






