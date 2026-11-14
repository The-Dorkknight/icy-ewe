# Required Notice: Copyright Matthew Armstrong (https://github.com/The-Dorkknight)
# Licensed under the PolyForm Noncommercial License 1.0.0. No warranty.
"""Draw the paper's illustrations (matplotlib, numpy, OpenCV). Numbers come from the
Scantastic write-ups (docs/research in the Scantastic repository); see each function."""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Wedge, FancyArrowPatch, Rectangle, Polygon
import cv2

OUT = sys.argv[1] if len(sys.argv) > 1 else "figures"
os.makedirs(OUT, exist_ok=True)
C = dict(coral="#FF6B6B", teal="#12B5A6", sun="#FFC23C", sky="#4D96FF", violet="#9B5DE5",
         lime="#5BC46A", ink="#22223B", grey="#8D99AE", paper="#FFFFFF", pale="#F4F6FB", pink="#FF8FB1")
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12, "axes.edgecolor": C["ink"],
                     "axes.labelcolor": C["ink"], "xtick.color": C["ink"], "ytick.color": C["ink"],
                     "axes.spines.top": False, "axes.spines.right": False})


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  ", name)


def box(ax, x, y, w, h, text, colour, fs=12, tc="white", r=0.06, bold=True):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.02,rounding_size={r}",
                                fc=colour, ec="none"))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=tc, fontsize=fs,
            fontweight="bold" if bold else "normal", wrap=True)


def arrow(ax, x0, y0, x1, y1, colour=C["ink"], lw=2.2, style="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=16,
                                 color=colour, lw=lw, linestyle=ls))


# 1. The whole pipeline
def pipeline():
    fig, ax = plt.subplots(figsize=(14, 4.6))
    ax.set_xlim(0, 13); ax.set_ylim(0, 4.6); ax.axis("off")
    steps = [("Depth\ncamera\nSR305 /\nD415", C["grey"]), ("Capture\nclean, trim,\ncut out\nsubject", C["sky"]),
             ("Chain\neach frame to\nthe last", C["violet"]), ("Loop closures\n+ pose graph", C["coral"]),
             ("Polish\nagainst the\nwhole model", C["teal"]), ("Fuse\n(TSDF) to a\nmesh", C["lime"]),
             ("STL / OBJ\n/ PLY", C["sun"])]
    for i, (t, c) in enumerate(steps):
        x = 0.15 + i * 1.83
        box(ax, x, 1.6, 1.62, 1.8, t, c, fs=10.5, tc=C["ink"] if c in (C["sun"], C["lime"]) else "white")
        if i:
            arrow(ax, x - 0.22, 2.5, x - 0.02, 2.5)
    ax.text(0.15 + 2 * 1.83, 3.65, "picture features check every step  ·  turntable: one fitted axis",
            fontsize=11, color=C["violet"], fontweight="bold")
    ax.add_patch(FancyBboxPatch((0.15 + 2 * 1.83, 0.25), 3 * 1.83 - 0.23, 1.1,
                                boxstyle="round,pad=0.02,rounding_size=0.08", fc=C["pale"], ec=C["coral"], lw=2, ls="--"))
    ax.text(0.15 + 2 * 1.83 + (3 * 1.83 - 0.23) / 2, 0.8, "over 90% of the build time is spent here\n(lining frames up with ICP)",
            ha="center", va="center", fontsize=11.5, color=C["coral"], fontweight="bold")
    save(fig, "fig-pipeline.png")


# 2. Where the time goes (0.11.0 profile of one made-up 24-frame handheld scan, 2-core machine)
def time_split():
    fig, ax = plt.subplots(figsize=(11, 3.6))
    parts = [("Chain", 27, C["violet"]), ("Loop closures", 60, C["coral"]), ("Polish", 24, C["teal"]),
             ("Fuse", 4, C["lime"]), ("Watertight", 7, C["sky"]), ("Preview", 5, C["sun"])]
    left = 0
    for name, s, col in parts:
        ax.barh(0, s, left=left, color=col, height=0.55)
        ax.text(left + s / 2, 0, f"{name}\n{s} s" if s > 8 else f"{s}", ha="center", va="center",
                color="white" if col not in (C["sun"], C["lime"]) else C["ink"], fontsize=11, fontweight="bold")
        left += s
    ax.annotate("lining up: 111 s", xy=(55, 0.33), xytext=(55, 0.75), ha="center", fontsize=12, color=C["ink"],
                fontweight="bold", arrowprops=dict(arrowstyle="-[,widthB=7.5", color=C["ink"]))
    ax.annotate("the mesh: 16 s", xy=(119, 0.33), xytext=(119, 0.75), ha="center", fontsize=12, color=C["ink"],
                fontweight="bold", arrowprops=dict(arrowstyle="-[,widthB=1.2", color=C["ink"]))
    ax.set_yticks([]); ax.set_xlabel("seconds (one made-up 24-frame handheld scan, 2-core machine)")
    ax.set_xlim(0, 130); ax.set_ylim(-0.5, 1.0)
    ax.spines["left"].set_visible(False)
    save(fig, "fig-time-split.png")


# 3. The two scan styles
def two_styles():
    fig, ax = plt.subplots(figsize=(13, 5.2))
    ax.set_xlim(0, 13); ax.set_ylim(0, 5.2); ax.axis("off")
    ax.text(0.1, 4.75, "Stitch while scanning (faster PCs)", fontsize=14, fontweight="bold", color=C["sky"])
    for i in range(12):
        x = 0.2 + i * 0.62
        ax.add_patch(Rectangle((x, 3.85), 0.5, 0.5, fc=C["sky"], ec="none", alpha=0.9))
        if i % 3 == 0:
            ax.add_patch(Circle((x + 0.25, 3.55), 0.11, fc=C["coral"]))
    ax.text(7.8, 4.1, "camera frames, tracked live\n(red dots: captures, each\nstarting where the tracker\nsaid the camera was)", fontsize=10.5, va="center")
    box(ax, 10.6, 3.75, 2.2, 0.75, "Build Mesh", C["lime"], tc=C["ink"])
    arrow(ax, 10.2, 4.1, 10.55, 4.1)
    ax.text(0.1, 2.6, "Record now, stitch afterwards (slow PCs, e.g. a 7th-gen i3)", fontsize=14, fontweight="bold", color=C["violet"])
    for i in range(12):
        x = 0.2 + i * 0.62
        ax.add_patch(Rectangle((x, 1.7), 0.5, 0.5, fc=C["violet"], ec="none", alpha=0.85))
    ax.text(7.8, 1.95, "frames only saved to disk,\nat most 10 a second", fontsize=10.5, va="center")
    box(ax, 0.2, 0.25, 4.5, 1.0, "After STOP, a separate program\ncleans, tracks and keeps\none frame per 6° or 3 cm", C["coral"], fs=10)
    box(ax, 5.2, 0.25, 2.8, 1.0, "out of memory?\nonly it dies: retry on\nevery 2nd frame", C["sun"], fs=10.5, tc=C["ink"])
    box(ax, 8.5, 0.25, 2.0, 1.0, "frames join\nthe scan", C["teal"], fs=11)
    box(ax, 10.9, 0.25, 1.9, 1.0, "Build Mesh", C["lime"], tc=C["ink"])
    for x0, x1 in ((4.75, 5.15), (8.05, 8.45), (10.55, 10.85)):
        arrow(ax, x0, 0.75, x1, 0.75)
    save(fig, "fig-two-styles.png")


# 4. Crash-proof stitching: memory budget and the retry ladder
def crashproof():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.5, 4.3), gridspec_kw=dict(width_ratios=[1.1, 1]))
    free = np.linspace(0, 8000, 300)
    budget = np.clip(free * 0.3 / 5.0, 40, 300)
    a1.fill_between(free / 1000, budget, color=C["teal"], alpha=0.25)
    a1.plot(free / 1000, budget, color=C["teal"], lw=3)
    a1.set_xlabel("free memory (GB)"); a1.set_ylabel("frames a stitch may hold")
    a1.set_title("Memory budget: 30% of free memory at 5 MB a frame,\nnever under 40 or over 300", fontsize=11.5, color=C["ink"])
    a1.axvline(2.0, color=C["coral"], ls="--"); a1.text(2.1, 60, "an 8 GB i3 with a\nbrowser open (~2 GB free)\n→ 120 frames", color=C["coral"], fontsize=10)
    a2.axis("off"); a2.set_xlim(0, 10); a2.set_ylim(0, 6)
    rows = [("Try 1: every frame", C["sky"], "×"), ("Try 2: every 2nd frame", C["violet"], "×"), ("Try 3: every 4th frame", C["lime"], "✓")]
    for i, (t, col, mark) in enumerate(rows):
        y = 4.6 - i * 1.55
        box(a2, 0.3, y, 6.3, 1.05, t, col, fs=12, tc="white" if col != C["lime"] else C["ink"])
        a2.text(7.2, y + 0.52, mark, fontsize=26, color=C["coral"] if mark == "×" else C["lime"], va="center", fontweight="bold")
    a2.text(7.9, 1.35, "the recording\nstays on disk\nwhatever happens", fontsize=11, color=C["ink"], va="center")
    a2.text(0.3, 0.05, "A stitch that dies before doing any work isn't blamed on memory.", fontsize=10, color=C["grey"])
    save(fig, "fig-crashproof.png")


# 5. Thinning a recording by motion
def thinning():
    rng = np.random.default_rng(4)
    n = 116
    t = np.linspace(0, 1, n)
    ang = np.cumsum(np.abs(rng.normal(1.0, 0.6, n)))
    ang = ang / ang[-1] * 150 - 75
    r = 0.45 + 0.02 * np.sin(t * 9)
    x, y = r * np.sin(np.radians(ang)), -r * np.cos(np.radians(ang))
    kept = [0]
    for i in range(1, n):
        da = abs(ang[i] - ang[kept[-1]]); dd = np.hypot(x[i] - x[kept[-1]], y[i] - y[kept[-1]])
        if da >= 6 or dd >= 0.03:
            kept.append(i)
    fig, ax = plt.subplots(figsize=(8.5, 5.4))
    ax.add_patch(Circle((0, 0), 0.08, fc=C["sun"], ec=C["ink"]))
    ax.text(0, 0, "object", ha="center", va="center", fontsize=10, fontweight="bold")
    ax.scatter(x, y, s=14, color=C["grey"], alpha=0.6, label=f"{n} recorded frames")
    ax.scatter(x[kept], y[kept], s=70, color=C["coral"], zorder=3, label=f"{len(kept)} kept (one per 6° or 3 cm)")
    for i in kept:
        ax.plot([x[i], 0.55 * x[i]], [y[i], 0.55 * y[i]], color=C["coral"], alpha=0.25, lw=1)
    ax.set_aspect("equal"); ax.axis("off")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=2, frameon=False, fontsize=11)
    ax.set_xlim(-0.6, 0.6); ax.set_ylim(-0.55, 0.15)
    ax.set_title("A 40-second handheld recording, seen from above (made-up camera path)", fontsize=12)
    save(fig, "fig-thinning.png")
    return len(kept)


# 6. Keyframe tracker
def keyframes():
    fig, ax = plt.subplots(figsize=(11, 3.8))
    ax.set_xlim(0, 11); ax.set_ylim(0, 3.8); ax.axis("off")
    xs = np.linspace(0.4, 10.6, 28)
    kf = [0, 7, 13, 20, 27]
    lost = (16, 17)
    for i, xx in enumerate(xs):
        col = C["grey"]
        if i in kf: col = C["violet"]
        if lost[0] <= i <= lost[1]: col = C["coral"]
        ax.add_patch(Rectangle((xx - 0.13, 1.6), 0.26, 0.5, fc=col, ec="none"))
    for k in kf:
        ax.text(xs[k], 2.35, "key", ha="center", color=C["violet"], fontweight="bold", fontsize=10)
    for i in range(1, 28):
        if lost[0] <= i <= lost[1]:
            continue
        k = max(j for j in kf if j <= i and j != i) if i not in kf else max([j for j in kf if j < i] or [0])
        ax.add_patch(FancyArrowPatch((xs[i], 1.55), (xs[k], 1.55), connectionstyle="arc3,rad=0.45",
                                     arrowstyle="-", color=C["sky"], lw=1, alpha=0.7))
    ax.text(xs[16] + 0.15, 2.85, "TRACKING LOST\n(camera covered)", color=C["coral"], ha="center", fontweight="bold", fontsize=10.5)
    ax.add_patch(FancyArrowPatch((xs[18], 2.2), (xs[7], 2.6), connectionstyle="arc3,rad=0.35",
                                 arrowstyle="-|>", mutation_scale=14, color=C["coral"], lw=2, ls="--"))
    ax.text(xs[11], 3.45, "found its way back by matching an older keyframe", ha="center", color=C["coral"], fontsize=10.5)
    ax.text(0.4, 0.55, "Each frame is matched to the current keyframe (blue arcs), not to the frame before, so small errors don't pile up.\n"
            "A new keyframe after 8°, 4 cm, or when fewer than 60 picture features still match.", fontsize=10.5, color=C["ink"])
    save(fig, "fig-keyframes.png")


# 7. The loop-closure rule
def loop_rule():
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    n = np.arange(0, 11)
    ax.plot(n, 2 + 0.25 * n, color=C["teal"], lw=3.5, marker="o", label="every step in between vouched for by the pictures")
    ax.plot(n, 2 + 5.0 * n, color=C["coral"], lw=3.5, marker="o", label="no step vouched for")
    ax.fill_between(n, 0, 2 + 0.25 * n, color=C["teal"], alpha=0.15)
    ax.set_xlabel("chain steps between the two frames"); ax.set_ylabel("most a closure may turn a frame (°)")
    ax.set_ylim(0, 30); ax.set_xlim(0, 10)
    ax.annotate("40 of 42 closures on the plain blob\nwere 10–40° out: a smooth\nsurface fitting itself in the wrong place",
                xy=(6, 3.5), xytext=(4.3, 16), fontsize=10.5, color=C["ink"],
                arrowprops=dict(arrowstyle="->", color=C["ink"]))
    ax.legend(frameon=False, loc="upper left", fontsize=10.5)
    ax.set_title("A loop closure the pictures can't confirm may only move a frame as far as the chain could have drifted\n"
                 "(and 8 mm + 2 mm per vouched step / + 30 mm per unvouched step)", fontsize=10.5)
    save(fig, "fig-loop-rule.png")


# 8. Turntable: one axis
def turntable():
    fig, ax = plt.subplots(figsize=(7.2, 6.4))
    ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Circle((0, 0), 1.0, fc=C["pale"], ec=C["grey"], lw=2))
    ax.add_patch(Circle((0, 0), 0.03, fc=C["ink"]))
    ax.text(0.05, -0.12, "fitted axis", fontsize=10)
    ang = np.radians(np.arange(0, 360, 30))
    for i, a in enumerate(ang):
        bad = i == 4
        r = 0.78
        x, y = r * np.cos(a), r * np.sin(a)
        if bad:
            ax.add_patch(Circle((x + 0.12, y - 0.1), 0.06, fc=C["coral"], ec="none"))
            ax.annotate("a step that doesn't fit the axis\nis tried again at the angle\nthe pictures suggest",
                        xy=(x + 0.12, y - 0.1), xytext=(-1.6, 1.15), fontsize=10, color=C["coral"],
                        arrowprops=dict(arrowstyle="->", color=C["coral"]))
            ax.add_patch(Circle((x, y), 0.06, fc="none", ec=C["teal"], lw=2, ls="--"))
        else:
            ax.add_patch(Circle((x, y), 0.06, fc=C["teal"], ec="none"))
        ax.text(1.12 * np.cos(a), 1.12 * np.sin(a), f"{i * 30}°", ha="center", va="center", fontsize=9, color=C["grey"])
    ax.add_patch(Wedge((0, 0), 0.45, 0, 30, fc=C["sun"], alpha=0.7))
    ax.text(0.47, 0.11, "each frame's pose =\nthe sum of the turns before it", fontsize=10)
    ax.add_patch(Rectangle((-0.25, -0.25), 0.5, 0.5, fc=C["sky"], alpha=0.8))
    ax.text(0, -0.37, "object", ha="center", fontsize=10)
    ax.set_xlim(-1.7, 1.7); ax.set_ylim(-1.4, 1.6)
    ax.set_title("Turntable mode, from above: every step is a turn about the same line", fontsize=12)
    save(fig, "fig-turntable.png")


# 9. A marker ring (illustration: an ArUco ring of the same kind)
def ring():
    d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    size = 1400
    img = np.full((size, size), 255, np.uint8)
    cx = cy = size // 2
    cv2.circle(img, (cx, cy), 610, 0, 3); cv2.circle(img, (cx, cy), 330, 0, 3)
    n = 12
    for i in range(n):
        a = 2 * np.pi * i / n
        m = cv2.aruco.generateImageMarker(d, i, 140)
        M = cv2.getRotationMatrix2D((70, 70), -np.degrees(a) - 90, 1.0)
        m = cv2.warpAffine(m, M, (140, 140), borderValue=255)
        x, y = int(cx + 470 * np.cos(a) - 70), int(cy + 470 * np.sin(a) - 70)
        img[y:y + 140, x:x + 140] = np.minimum(img[y:y + 140, x:x + 140], m)
    cv2.putText(img, "object here", (cx - 150, cy + 12), cv2.FONT_HERSHEY_SIMPLEX, 1.4, 120, 3)
    rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    rgb[img < 128] = (40, 40, 60)
    cv2.imwrite(os.path.join(OUT, "fig-ring.png"), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
    print("   fig-ring.png")


# 10. The cropped polish
def crop():
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    ax.set_aspect("equal"); ax.axis("off")
    t = np.linspace(0, 2 * np.pi, 400)
    ax.fill(1.8 * np.cos(t), 1.25 * np.sin(t), color=C["pale"], ec=C["grey"], lw=2)
    ax.text(-1.55, 1.05, "the whole model\n(every frame together)", fontsize=10.5, color=C["grey"])
    fx, fy, fw, fh = 0.2, -0.55, 0.9, 0.75
    d = 0.12
    for k, col, lab in ((5, C["sun"], "5× the match distance: what is kept"), (3, C["lime"], "3×: the most that can matter"), (1, C["teal"], "1×: where matches are made")):
        ax.add_patch(Rectangle((fx - k * d, fy - k * d), fw + 2 * k * d, fh + 2 * k * d, fc=col, alpha=0.35, ec=col, lw=2))
    ax.add_patch(Rectangle((fx, fy), fw, fh, fc=C["coral"], alpha=0.9))
    ax.text(fx + fw / 2, fy + fh / 2, "one frame", ha="center", va="center", color="white", fontweight="bold")
    for k, col, lab in ((5, C["sun"], "5×: what is kept"), (3, C["lime"], "3×: the most that can matter"), (1, C["teal"], "1×: where matches are made")):
        ax.text(fx + fw + k * d + 0.05, fy + fh + k * d - 0.05, lab, fontsize=9.5, color=C["ink"])
    ax.text(-1.95, -1.65, "Colour ICP works out a colour gradient for every target point from its neighbours within 2×, on every call.\n"
            "Points further than 3× can't change the answer. If the frame moves more than the spare 2×, or the answer scores\n"
            "differently against the whole model, it is done again on the whole model. Same poses (to 1e-14), polish ~25% quicker.",
            fontsize=9.5, color=C["ink"])
    ax.set_xlim(-2, 2.6); ax.set_ylim(-1.9, 1.4)
    save(fig, "fig-crop.png")


# 11. Helpers side by side
def helpers():
    fig, ax = plt.subplots(figsize=(12, 5.0))
    ax.set_xlim(0, 12); ax.set_ylim(-0.2, 4.8); ax.axis("off")
    box(ax, 0.3, 1.6, 3.0, 1.6, "Building\nprocess\n(works through\ntasks too)", C["violet"], fs=11.5)
    for i in range(3):
        y = 3.4 - i * 1.35
        box(ax, 6.6, y, 3.0, 0.95, f"Helper {i + 1}\n(own copy of the frames)", C["sky"], fs=10.5)
        arrow(ax, 3.35, 2.4, 6.55, y + 0.48, colour=C["grey"], lw=1.6, style="<|-|>")
    ax.text(4.2, 4.1, "tasks out, answers back,\nput back in the original order", fontsize=10.5, color=C["ink"])
    box(ax, 9.9, 1.5, 1.95, 1.9, "same answer\nas one process\n(to 1e-13)", C["lime"], fs=10.5, tc=C["ink"])
    ax.text(0.3, 0.45, "A helper ends when its pipe breaks or its watchdog sees the builder gone (Cancel).", fontsize=10.5, color=C["ink"])
    ax.text(0.3, 0.02, "A helper that dies or fails only costs time: the builder redoes its task.", fontsize=10.5, color=C["ink"])
    save(fig, "fig-helpers.png")


# 12. Results across versions (made-up scans, see docs/research/bench-results in the app repo)
def results():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.5, 4.4))
    vers = ["0.8.1", "0.9.0", "0.10.0\n(rerun)", "0.11.0", "0.11.0\ncard method"]
    fails = [20, 0, 1, 1, 1]
    cols = [C["coral"], C["teal"], C["sky"], C["violet"], C["pink"]]
    a1.bar(vers, fails, color=cols)
    for i, f in enumerate(fails):
        a1.text(i, f + 0.4, str(f), ha="center", fontweight="bold")
    a1.set_ylabel("scans failed (of 20)"); a1.set_ylim(0, 23)
    a1.set_title("Handheld, 20 held-out made-up scans\n(fail = any frame more than 3 mm out)", fontsize=11)
    names = ["turntable\n(40 scans)", "handheld\nheld-out", "live tracking\nheld-out", "record now,\nstitch later"]
    worst = [0.6, 0.9, 1.0, 0.9]
    a2.bar(names, worst, color=[C["teal"], C["sky"], C["violet"], C["sun"]])
    for i, w in enumerate(worst):
        a2.text(i, w + 0.03, f"{w} mm", ha="center", fontweight="bold")
    a2.set_ylabel("typical worst frame (mm)"); a2.set_ylim(0, 1.3)
    a2.set_title("How far out the worst frame typically was\n(scans that passed)", fontsize=11)
    save(fig, "fig-results.png")


# 13. Speed profiles card
def profiles():
    fig, ax = plt.subplots(figsize=(12.5, 3.9))
    ax.set_xlim(0, 12.5); ax.set_ylim(0, 3.9); ax.axis("off")
    cards = [("Potato", C["sun"], "1 alignment at a time\nlowest priority\nno graphics card", "Auto: under 4 cores\nor 12 GB (7th-gen i3)"),
             ("Moderate", C["sky"], "half the cores\nbelow-normal priority\nno graphics card", "Auto: in between"),
             ("Extreme", C["coral"], "every core\nnormal priority\nNvidia card on Linux,\nonce its test passes", "Auto: 8+ cores, 16+ GB")]
    for i, (name, col, body, who) in enumerate(cards):
        x = 0.25 + i * 4.1
        box(ax, x, 0.25, 3.8, 3.4, "", col)
        ax.text(x + 1.9, 3.15, name, ha="center", fontsize=17, fontweight="bold", color="white" if col != C["sun"] else C["ink"])
        ax.text(x + 1.9, 1.95, body, ha="center", va="center", fontsize=11.5, color="white" if col != C["sun"] else C["ink"])
        ax.text(x + 1.9, 0.6, who, ha="center", va="center", fontsize=10.5, color="white" if col != C["sun"] else C["ink"], style="italic")
    save(fig, "fig-profiles.png")


# 14. Tracking lost banner, drawn by the app's own function on a made-up frame
def tracking_lost():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))
    import stream_pipeline as sp
    src = sp.SyntheticSource(n=3, size=(480, 640))
    frame = list(src)[1]
    img = cv2.cvtColor(np.ascontiguousarray(frame["color"]), cv2.COLOR_RGB2BGR) if frame["color"].shape[-1] == 3 else frame["color"]
    os.environ["SR305_SKIP_BOOTSTRAP"] = "1"
    argv, sys.argv = sys.argv, ["app"]
    import scantastic as A
    sys.argv = argv
    img = A.draw_tracking_lost(img.copy())
    cv2.imwrite(os.path.join(OUT, "fig-tracking-lost.png"), img)
    print("   fig-tracking-lost.png")


if __name__ == "__main__":
    pipeline(); time_split(); two_styles(); crashproof(); print("kept", thinning()); keyframes()
    loop_rule(); turntable(); ring(); crop(); helpers(); results(); profiles(); tracking_lost()
