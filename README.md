## A correction to Keil’s algorithm for minimum convex decomposition of simple polygons without Steiner points

Let $P$ be a simple polygon in the plane with $n$ vertices $p_0$, $p_1$, …, $p_{n-1}$ in counterclockwise order, $r$ of which are reflex vertices with interior angles greater than $\pi$.
A minimum convex decomposition of $P$ without Steiner points is a partition of $P$ into the smallest possible number of convex regions, each of whose vertices is a vertex of $P$.

Relatively little research has addressed exact solution methods for this problem.
Greene (1983) gave the first known exact algorithm with a running time of $O(n^2 r^2)$.
Keil (1985) subsequently proposed a dynamic programming algorithm that solves the problem optimally in $O(n r^2 \log n)$ time.
Keil and Snoeyink (2002) later presented an efficient implementation that improves the running time to $O(n r^2)$.
To the best of our knowledge, Keil’s algorithm remains the most efficient known exact algorithm for this problem.

We show that when the input polygon contains collinear vertices, the algorithm may fail to find a feasible decomposition or return a non-minimum one. Two examples expose the underlying issue: certain faces of the canonical triangulation are not recognized as base triangles because some of their sides are not valid diagonals.

To correct this issue, we extend the definition of a diagonal to include any segment joining two non-adjacent vertices that is contained in the closure of the polygon, allowing contact with its boundary. The revised formulation permits spiky subpolygons and degenerate base triangles, while leaving the remainder of the algorithm unchanged.

For a detailed description of the correction, see [mcd.pdf](./mcd.pdf).

## Repository

This repository contains the following:

- `mcd-demo-fixed`: a corrected version of the Java demonstration program by [Jack Snoeyink](https://www.cs.unc.edu/~snoeyink/demos/convdecomp)
- `mcd`: a lightweight Python implementation of the corrected algorithm

## Citation

If you use this repository in academic work, please cite it as follows:

> Jin, B. (2026). A correction to Keil’s algorithm for minimum convex decomposition of simple polygons without Steiner points. https://github.com/jinboszu/mcd

BibTeX:

```bibtex
@misc{jin2026mcd,
	author       = {Jin, Bo},
	title        = {A correction to {Keil}'s algorithm for minimum convex decomposition of simple polygons without {Steiner} points},
	year         = {2026},
	url          = {https://github.com/jinboszu/mcd},
	howpublished = {\url{https://github.com/jinboszu/mcd}}
}
```

## References

- Greene, D. H. (1983). The decomposition of polygons into convex parts. In F. P. Preparata (Ed.), *Computational Geometry* (pp. 235–259). JAI Press.
- Keil, J. M. (1985). Decomposing a polygon into simpler components. *SIAM Journal on Computing*, *14*(4), 799–817. https://doi.org/10.1137/0214056
- Keil, M., & Snoeyink, J. (2002). On the time bound for convex decomposition of simple polygons. *International Journal of Computational Geometry & Applications*, *12*(03), 181–192. https://doi.org/10.1142/S0218195902000803
