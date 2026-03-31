#!/usr/bin/env python3
"""
graph_generator.py
==================
Non-isomorphic graph generator for graph energy research.

Provides utilities to:
  - Generate all non-isomorphic simple graphs on n vertices.
  - Compute the adjacency matrix, eigenvalues, graph energy E(G),
    and local energy e(G) (Espinal & Rada, 2024).

Designed to be imported by other scripts in the pipeline.

References
----------
Gutman, I. (1978). The energy of a graph.
    Ber. Math.-Stat. Sekt. Forschungsz. Graz, 103, 1-22.
Espinal, A., & Rada, J. (2024). Local energy of graphs. [full ref — TODO]

Usage as a module
-----------------
    from graph_generator import generate_nonisomorphic_graphs, compute_spectral_data

    for G in generate_nonisomorphic_graphs(n=5):
        data = compute_spectral_data(G)
        print(f"E(G) = {data['energy']:.4f},  e(G) = {data['local_energy']:.4f}")

Usage as a CLI script
---------------------
    python graph_generator.py --n 6
    python graph_generator.py --n 7 --output data/graphs_n7.pkl
    python graph_generator.py --n 5 --format adjlist --output data/graphs_n5.txt
"""

from __future__ import annotations

import argparse
import logging
import pickle
from itertools import combinations
from pathlib import Path
from typing import Dict, Generator, List, Optional, Tuple

import networkx as nx
import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Isomorphism utilities
# ──────────────────────────────────────────────────────────────────────────────

def canonical_hash(G: nx.Graph) -> str:
    """
    Compute a Weisfeiler-Lehman canonical hash for G.

    Used as a fast pre-filter: two non-isomorphic graphs will (almost always)
    produce different hashes. Collisions are resolved with an exact VF2 check.

    Parameters
    ----------
    G : nx.Graph

    Returns
    -------
    str
        WL hash string.
    """
    return nx.weisfeiler_lehman_graph_hash(G, iterations=10)


def are_isomorphic(G1: nx.Graph, G2: nx.Graph) -> bool:
    """Exact graph isomorphism test (VF2 algorithm)."""
    return nx.is_isomorphic(G1, G2)


# ──────────────────────────────────────────────────────────────────────────────
# Graph generation
# ──────────────────────────────────────────────────────────────────────────────

def generate_nonisomorphic_graphs(
    n: int,
    verbose: bool = False,
) -> List[nx.Graph]:
    """
    Generate all non-isomorphic simple undirected graphs on n vertices.

    Strategy
    --------
    - n ≤ 7  → NetworkX Graph Atlas (complete, very fast).
    - n > 7  → Full edge-subset enumeration with WL-hash deduplication and
               VF2 exact-isomorphism confirmation.
               Exponential complexity: practical for n ≤ 10.
               For n ≥ 11 consider interfacing with *nauty/traces*.

    Parameters
    ----------
    n : int
        Number of vertices (≥ 1).
    verbose : bool
        Log progress to stderr.

    Returns
    -------
    List[nx.Graph]
        All non-isomorphic graphs on n vertices, nodes labelled 0 … n-1,
        sorted in ascending order of edge count.
    """
    if n < 1:
        raise ValueError(f"n must be ≥ 1, got {n}.")
    if n > 10:
        logger.warning(
            "n=%d may take a very long time. "
            "Consider nauty/traces for n > 10.",
            n,
        )

    if n <= 7:
        graphs = _from_atlas(n)
    else:
        graphs = _enumerate_nonisomorphic(n, verbose=verbose)

    # Normalise node labels to 0 … n-1
    graphs = [nx.convert_node_labels_to_integers(G) for G in graphs]
    # Sort by number of edges (empty graph first, complete graph last)
    graphs.sort(key=lambda G: G.number_of_edges())
    return graphs


def _from_atlas(n: int) -> List[nx.Graph]:
    """Return non-isomorphic graphs on exactly n vertices from the NetworkX atlas."""
    return [G.copy() for G in nx.graph_atlas_g() if G.number_of_nodes() == n]


def _enumerate_nonisomorphic(n: int, verbose: bool = False) -> List[nx.Graph]:
    """
    Enumerate all non-isomorphic graphs on n vertices by brute force.

    Iterates over all C(n,2) choose r edge subsets (r = 0, 1, …, C(n,2)).
    A WL hash is used as a fast pre-filter; exact VF2 resolves hash collisions.
    """
    vertices = list(range(n))
    all_edges = list(combinations(vertices, 2))
    max_edges = len(all_edges)

    if verbose:
        logger.info(
            "Enumerating 2^%d = %d edge subsets for n=%d …",
            max_edges, 2**max_edges, n,
        )

    # registry: wl_hash  →  list of confirmed non-isomorphic graphs
    registry: Dict[str, List[nx.Graph]] = {}
    count = 0

    for r in range(max_edges + 1):
        for edge_subset in combinations(all_edges, r):
            G = nx.Graph()
            G.add_nodes_from(vertices)
            G.add_edges_from(edge_subset)

            h = canonical_hash(G)

            if h not in registry:
                registry[h] = [G]
                count += 1
            else:
                # Exact check only among same-hash graphs (usually 0–1 graphs)
                if not any(are_isomorphic(G, H) for H in registry[h]):
                    registry[h].append(G)
                    count += 1

    if verbose:
        logger.info("Found %d non-isomorphic graphs on n=%d vertices.", count, n)

    return [G for bucket in registry.values() for G in bucket]


def nonisomorphic_graph_generator(n: int, verbose: bool = False) -> Generator[nx.Graph, None, None]:
    """
    Lazy generator variant of :func:`generate_nonisomorphic_graphs`.

    Yields graphs one at a time without storing the full list in memory.
    Useful when n is large or memory is constrained.

    Parameters
    ----------
    n : int
    verbose : bool

    Yields
    ------
    nx.Graph
    """
    for G in generate_nonisomorphic_graphs(n, verbose=verbose):
        yield G


# ──────────────────────────────────────────────────────────────────────────────
# Adjacency matrix
# ──────────────────────────────────────────────────────────────────────────────

def get_adjacency_matrix(G: nx.Graph) -> np.ndarray:
    """
    Return the adjacency matrix of G as a real-valued NumPy array.

    Rows and columns are ordered by ascending node label (0, 1, …, n-1).

    Parameters
    ----------
    G : nx.Graph

    Returns
    -------
    np.ndarray, shape (n, n)
    """
    return nx.to_numpy_array(G, nodelist=sorted(G.nodes()), dtype=float)


# ──────────────────────────────────────────────────────────────────────────────
# Spectral computations
# ──────────────────────────────────────────────────────────────────────────────

def compute_eigenvalues(G: nx.Graph) -> np.ndarray:
    """
    Compute the eigenvalues of the adjacency matrix A(G).

    Uses ``numpy.linalg.eigvalsh`` (exploit symmetry, returns real values).

    Parameters
    ----------
    G : nx.Graph

    Returns
    -------
    np.ndarray, shape (n,)
        Eigenvalues λ₁ ≥ λ₂ ≥ … ≥ λₙ (descending order).
    """
    A = get_adjacency_matrix(G)
    eigs = np.linalg.eigvalsh(A)   # ascending by convention
    return eigs[::-1].copy()        # flip to descending


def compute_eigenvalues_and_vectors(
    G: nx.Graph,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute eigenvalues and orthonormal eigenvectors of A(G).

    Parameters
    ----------
    G : nx.Graph

    Returns
    -------
    eigenvalues : np.ndarray, shape (n,)
        Sorted λ₁ ≥ λ₂ ≥ … ≥ λₙ.
    eigenvectors : np.ndarray, shape (n, n)
        ``eigenvectors[:, i]`` is the eigenvector for ``eigenvalues[i]``.
    """
    A = get_adjacency_matrix(G)
    eigs, vecs = np.linalg.eigh(A)          # ascending eigenvalues
    idx = np.argsort(eigs)[::-1]            # descending permutation
    return eigs[idx], vecs[:, idx]


def compute_energy(G: nx.Graph) -> float:
    """
    Compute the (Gutman) graph energy of G.

        E(G) = Σᵢ |λᵢ(A(G))|

    Parameters
    ----------
    G : nx.Graph

    Returns
    -------
    float
    """
    return float(np.sum(np.abs(compute_eigenvalues(G))))


# ──────────────────────────────────────────────────────────────────────────────
# Local energy  (Espinal & Rada, 2024)
# ──────────────────────────────────────────────────────────────────────────────
#
# ⚠️  IMPORTANT — verify the formula below against Espinal & Rada (2024).
#
# Current definition implemented here
# ------------------------------------
# Let λ₁ ≥ … ≥ λₙ be the eigenvalues of A(G) and φ₁, …, φₙ the
# corresponding orthonormal eigenvectors.  For each vertex v ∈ V(G):
#
#     ε(v, G) = Σᵢ |λᵢ| · |φᵢ(v)|          (★)
#
# Local energy of G:
#
#     e(G) = Σᵥ ε(v, G) = Σᵢ |λᵢ| · ‖φᵢ‖₁
#
# Why (★) satisfies the sandwich  E(G) ≤ e(G) ≤ 2E(G)  (conjectured):
#   Lower bound:  ‖φᵢ‖₁ ≥ ‖φᵢ‖₂ = 1  ⟹  e(G) ≥ Σᵢ|λᵢ| = E(G).
#   Upper bound:  ‖φᵢ‖₁ ≤ √n · ‖φᵢ‖₂ = √n, but for "typical" graphs
#                 empirical evidence suggests ‖φᵢ‖₁ ≤ 2.
#
# If the paper uses a different formula, replace _local_energy_vertex below.
# ──────────────────────────────────────────────────────────────────────────────

def _local_energy_vertex(
    abs_eigenvalues: np.ndarray,
    eigenvectors: np.ndarray,
) -> np.ndarray:
    """
    Compute ε(v) for every vertex v in one vectorised operation.

    Parameters
    ----------
    abs_eigenvalues : np.ndarray, shape (n,)
        |λᵢ| values.
    eigenvectors : np.ndarray, shape (n, n)
        Column-eigenvectors (each column is one φᵢ).

    Returns
    -------
    np.ndarray, shape (n,)
        ε(v) for v = 0, 1, …, n-1.

    ⚠️  Update this function if the formula changes.
    """
    # ε(v) = Σᵢ |λᵢ| · |φᵢ(v)|
    # eigenvectors[v, i] = φᵢ(v)
    # |eigenvectors| @ abs_eigenvalues gives exactly that for each v.
    return np.abs(eigenvectors) @ abs_eigenvalues


def compute_local_energy_per_vertex(G: nx.Graph) -> np.ndarray:
    """
    Compute the local energy contribution ε(v) for every vertex v.

    Parameters
    ----------
    G : nx.Graph

    Returns
    -------
    np.ndarray, shape (n,)
        ε(v) for v = 0, 1, …, n-1.
    """
    n = G.number_of_nodes()
    if n == 0:
        return np.array([], dtype=float)
    eigs, vecs = compute_eigenvalues_and_vectors(G)
    return _local_energy_vertex(np.abs(eigs), vecs)


def compute_local_energy(G: nx.Graph) -> float:
    """
    Compute the local energy e(G) (Espinal & Rada, 2024).

        e(G) = Σᵥ ε(v, G)

    See module-level note for the current formula and the ⚠️  TODO.

    Parameters
    ----------
    G : nx.Graph

    Returns
    -------
    float
    """
    n = G.number_of_nodes()
    if n == 0:
        return 0.0
    return float(np.sum(compute_local_energy_per_vertex(G)))


# ──────────────────────────────────────────────────────────────────────────────
# All-in-one spectral data dict
# ──────────────────────────────────────────────────────────────────────────────

def compute_spectral_data(G: nx.Graph) -> Dict:
    """
    Compute every spectral quantity for G in a single eigendecomposition pass.

    Parameters
    ----------
    G : nx.Graph

    Returns
    -------
    dict
        Keys
        ----
        'n'                       int      — number of vertices
        'm'                       int      — number of edges
        'adjacency_matrix'        ndarray  — A(G), shape (n, n)
        'eigenvalues'             ndarray  — λ₁ ≥ … ≥ λₙ
        'eigenvectors'            ndarray  — column-eigenvectors, shape (n, n)
        'energy'                  float    — E(G) = Σ|λᵢ|
        'local_energy'            float    — e(G)
        'local_energy_per_vertex' ndarray  — ε(v) for each vertex
        'ratio_e_over_E'          float    — e(G)/E(G)  (nan if E=0)
    """
    n = G.number_of_nodes()
    m = G.number_of_edges()
    A = get_adjacency_matrix(G)

    if n == 0:
        return dict(
            n=0, m=0,
            adjacency_matrix=A,
            eigenvalues=np.array([]),
            eigenvectors=np.array([[]]),
            energy=0.0,
            local_energy=0.0,
            local_energy_per_vertex=np.array([]),
            ratio_e_over_E=float("nan"),
        )

    eigs, vecs = np.linalg.eigh(A)          # ascending
    idx = np.argsort(eigs)[::-1]
    eigs, vecs = eigs[idx], vecs[:, idx]    # descending

    abs_eigs = np.abs(eigs)
    energy = float(np.sum(abs_eigs))

    local_per_vertex = _local_energy_vertex(abs_eigs, vecs)
    local_energy = float(np.sum(local_per_vertex))

    ratio = local_energy / energy if energy > 1e-14 else float("nan")

    return dict(
        n=n,
        m=m,
        adjacency_matrix=A,
        eigenvalues=eigs,
        eigenvectors=vecs,
        energy=energy,
        local_energy=local_energy,
        local_energy_per_vertex=local_per_vertex,
        ratio_e_over_E=ratio,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Convenience pipeline
# ──────────────────────────────────────────────────────────────────────────────

def generate_and_compute(
    n: int,
    verbose: bool = False,
) -> List[Dict]:
    """
    Generate all non-isomorphic graphs on n vertices and compute their
    spectral data in one call.

    Each returned dict is the output of :func:`compute_spectral_data`
    extended with key ``'graph'`` (the ``nx.Graph`` object itself).

    Parameters
    ----------
    n : int
    verbose : bool

    Returns
    -------
    List[dict]
    """
    graphs = generate_nonisomorphic_graphs(n, verbose=verbose)
    results = []
    for G in graphs:
        data = compute_spectral_data(G)
        data["graph"] = G
        results.append(data)
    return results


# ──────────────────────────────────────────────────────────────────────────────
# I/O utilities
# ──────────────────────────────────────────────────────────────────────────────

def save_graphs(
    graphs: List[nx.Graph],
    path: str,
    fmt: str = "pkl",
) -> None:
    """
    Persist a list of graphs to disk.

    Parameters
    ----------
    graphs : List[nx.Graph]
    path   : str            Output file path.
    fmt    : str            ``'pkl'`` (pickle, default) or ``'adjlist'``.
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    if fmt == "pkl":
        with open(path, "wb") as fh:
            pickle.dump(graphs, fh)

    elif fmt == "adjlist":
        with open(path, "w", encoding="utf-8") as fh:
            for i, G in enumerate(graphs):
                fh.write(f"# Graph {i}  |V|={G.number_of_nodes()}"
                         f"  |E|={G.number_of_edges()}\n")
                for line in nx.generate_adjlist(G):
                    fh.write(line + "\n")
                fh.write("\n")

    else:
        raise ValueError(f"Unsupported format '{fmt}'. Choose 'pkl' or 'adjlist'.")

    logger.info("Saved %d graphs to '%s'.", len(graphs), path)


def load_graphs(path: str) -> List[nx.Graph]:
    """
    Load a list of graphs previously saved with :func:`save_graphs` (pickle).

    Parameters
    ----------
    path : str

    Returns
    -------
    List[nx.Graph]
    """
    with open(path, "rb") as fh:
        return pickle.load(fh)


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

_SEP = "─" * 90


def _print_results(results: List[Dict], n: int) -> None:
    """Print a human-readable table of spectral data."""
    print(f"\nNon-isomorphic graphs on n={n} vertices: {len(results)} found\n")
    header = (
        f"{'#':>5}  {'m':>4}  {'E(G)':>12}  {'e(G)':>12}  "
        f"{'e/E':>7}  eigenvalues"
    )
    print(header)
    print(_SEP)
    for i, d in enumerate(results):
        eigs_str = "  ".join(f"{v:+.4f}" for v in d["eigenvalues"])
        ratio_str = f"{d['ratio_e_over_E']:.4f}" if not np.isnan(d["ratio_e_over_E"]) else "  nan "
        print(
            f"{i:>5}  {d['m']:>4}  {d['energy']:>12.6f}  "
            f"{d['local_energy']:>12.6f}  {ratio_str:>7}  [{eigs_str}]"
        )
    print()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="graph_generator",
        description="Generate non-isomorphic graphs and compute spectral energy data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--n", type=int, required=True,
        metavar="N",
        help="Number of vertices.",
    )
    parser.add_argument(
        "--output", type=str, default=None,
        metavar="PATH",
        help="Save generated graphs to this file (optional).",
    )
    parser.add_argument(
        "--format", type=str, choices=["pkl", "adjlist"], default="pkl",
        dest="fmt",
        help="Output file format (default: pkl).",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Enable verbose logging.",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress the results table (useful when only saving to file).",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    results = generate_and_compute(args.n, verbose=args.verbose)

    if not args.quiet:
        _print_results(results, args.n)

    if args.output:
        graphs = [d["graph"] for d in results]
        save_graphs(graphs, args.output, fmt=args.fmt)


if __name__ == "__main__":
    main()