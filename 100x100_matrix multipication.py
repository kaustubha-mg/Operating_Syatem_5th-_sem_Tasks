import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
def generate_matrices(n, m, k, seed=7):
    rng = np.random.default_rng(seed)
    A = rng.integers(1, 10, size=(n, m)).astype(np.float64)
    B = rng.integers(1, 10, size=(m, k)).astype(np.float64)
    return A, B
def build_animation(A, B, out_path="matrix_mult_full_100x100.gif",
                     target_frames=220, fps=18, dpi=90, figsize=(13, 5)):
    n, m = A.shape
    m2, k = B.shape
    assert m == m2
    expected = A @ B  # ground truth, also used to fix the color scale
    vmin, vmax = float(expected.min()), float(expected.max())
    C = np.full((n, k), np.nan)
    total_cells = n * k
    batch = max(1, total_cells // target_frames)
    fig, (axA, axB, axC) = plt.subplots(1, 3, figsize=figsize)
    fig.suptitle(
        f"Matrix Multiplication at Full Scale: A ({n}\u00d7{m}) @ B ({m}\u00d7{k}) = C ({n}\u00d7{k})",
        fontsize=14, fontweight="bold"
    )
    for ax, title in ((axA, "A"), (axB, "B"), (axC, "C = A @ B")):
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.set_xticks([])
        ax.set_yticks([])
    axA.imshow(A, cmap="Blues", vmin=A.min(), vmax=A.max())
    axB.imshow(B, cmap="Blues", vmin=B.min(), vmax=B.max())
    im_c = axC.imshow(C, cmap="viridis", vmin=vmin, vmax=vmax)
    for ax in (axA, axB, axC):
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color("#666")
    row_rect = Rectangle((-0.5, -0.5), m, 1, fill=True, facecolor="#ffeb3b",
                          alpha=0.45, edgecolor="#f57f17", linewidth=2)
    axA.add_patch(row_rect)
    col_rect = Rectangle((-0.5, -0.5), 1, m, fill=True, facecolor="#00e5ff",
                          alpha=0.45, edgecolor="#00838f", linewidth=2)
    axB.add_patch(col_rect)
    active_rect = Rectangle((-0.5, -0.5), 1, 1, fill=False,
                             edgecolor="#ff1744", linewidth=2)
    axC.add_patch(active_rect)
    progress_text = fig.text(0.5, 0.02, "", ha="center", va="center", fontsize=11)
    steps = [(i, j) for i in range(n) for j in range(k)]
    n_frames = (len(steps) + batch - 1) // batch
    def update(frame_idx):
        start = frame_idx * batch
        end = min(start + batch, len(steps))
        batch_steps = steps[start:end]
        for (i, j) in batch_steps:
            C[i, j] = expected[i, j]
        last_i, last_j = batch_steps[-1]
        first_j_in_row = batch_steps[0][1] if batch_steps[0][0] == last_i else 0
        j_lo = min(j for (i, j) in batch_steps if i == last_i)
        j_hi = max(j for (i, j) in batch_steps if i == last_i)
        row_rect.set_xy((-0.5, last_i - 0.5))
        col_rect.set_xy((j_lo - 0.5, -0.5))
        col_rect.set_width(j_hi - j_lo + 1)
        active_rect.set_xy((last_j - 0.5, last_i - 0.5))
        im_c.set_data(C)
        done = int(np.count_nonzero(~np.isnan(C)))
        progress_text.set_text(
            f"row {last_i}, cols {j_lo}-{j_hi}  |  {done}/{total_cells} cells computed "
            f"({100*done/total_cells:.0f}%)"
        )
        return [im_c, row_rect, col_rect, active_rect, progress_text]
    ani = animation.FuncAnimation(
        fig, update, frames=n_frames, interval=1000 / fps, blit=False, repeat=False
    )
    plt.tight_layout(rect=[0, 0.05, 1, 0.94])
    ani.save(out_path, writer="pillow", fps=fps, dpi=dpi)
    plt.close(fig)
    return out_path, n_frames
def main():
    parser = argparse.ArgumentParser(description="Full-scale 100x100 matrix multiplication animation")
    parser.add_argument("--n", type=int, default=100)
    parser.add_argument("--m", type=int, default=100)
    parser.add_argument("--k", type=int, default=100)
    parser.add_argument("--frames", type=int, default=220, help="target number of animation frames")
    parser.add_argument("--fps", type=int, default=18)
    parser.add_argument("--out", type=str, default="matrix_mult_full_100x100.gif")
    args = parser.parse_args()
    assert args.n >= 100 and args.m >= 100 and args.k >= 100, "Matrices must be at least 100x100"
    print(f"Generating A ({args.n}x{args.m}) and B ({args.m}x{args.k}) ...")
    A, B = generate_matrices(args.n, args.m, args.k)
    print("Building full-scale animation (this may take a little while) ...")
    path, n_frames = build_animation(A, B, out_path=args.out,
                                      target_frames=args.frames, fps=args.fps)
    print(f"Animation saved to: {path} ({n_frames} frames)")
if __name__ == "__main__":
    main()
