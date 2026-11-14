"""Screenshots of the real app window (Scantastic as attached, 0.10.0 window) from made-up data.
    DISPLAY=:99 python3.12 shots.py GROUP OUTDIR"""
import os, sys, time, tempfile, subprocess
GROUP, OUT = sys.argv[1], os.path.abspath(sys.argv[2])
APP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app")
os.environ["SR305_SKIP_BOOTSTRAP"] = "1"
sys.path.insert(0, APP)
sys.argv = ["app", "--scans-dir", "/home/you/scantastic/scans"] + (["--plain"] if GROUP == "plain" else [])
import numpy as np
import tkinter as tk
from tkinter import messagebox
from PIL import Image
import scantastic as A
import open3d as o3d

A.SETTINGS_PATH = os.path.join(tempfile.mkdtemp(), "settings.json")
A.SENSOR_CHECK_DIR = "/home/you/scantastic/sensor_check"
for name in ("showerror", "showinfo", "showwarning"):
    setattr(messagebox, name, lambda *a, **k: None)
A.speed = getattr(A, "speed", None)
root = tk.Tk()
app = A.ScannerApp(root)
scratch = tempfile.mkdtemp()


def pump(seconds=0.3):
    end = time.time() + seconds
    while time.time() < end:
        root.update()
        time.sleep(0.01)


def shot(name, window=None):
    pump(0.3)
    grab = os.path.join(scratch, name + ".png")
    subprocess.run(["import", "-window", "root", grab], check=True)
    w = window or root
    x, y, width, height = w.winfo_rootx(), w.winfo_rooty(), w.winfo_width(), w.winfo_height()
    Image.open(grab).convert("RGB").crop((x, y, x + width, y + height)).save(os.path.join(OUT, name + ".png"))
    print("  ", name, width, height)


def scroll_panel(fraction):
    app._side_panel.master.yview_moveto(fraction)
    pump(0.4)


def made_up_scan(n=14, far_m=0.60, voxel_m=0.002):
    import stream_pipeline as sp
    source = sp.SyntheticSource(n=n, size=(360, 480), noise_m=0.002, holes=0.02, orbit_deg=60)
    core = o3d.core
    grid = o3d.t.geometry.VoxelBlockGrid(("tsdf", "weight", "color"), (core.float32, core.float32, core.float32),
                                         ((1), (1), (3)), voxel_m, 16, 60000, core.Device("CPU:0"))
    for frame, pose in zip(source, source.poses):
        depth = frame["depth"].copy()
        depth[depth > far_m * 1000] = 0
        d = o3d.t.geometry.Image(core.Tensor(np.ascontiguousarray(depth)))
        c = o3d.t.geometry.Image(core.Tensor(np.ascontiguousarray(frame["color"])))
        k = core.Tensor(frame["K"], core.float64)
        ext = core.Tensor(np.linalg.inv(pose), core.float64)
        blocks = grid.compute_unique_block_coordinates(d, k, ext, 1000.0, far_m)
        grid.integrate(blocks, d, c, k, k, ext, 1000.0, far_m)
    mesh = grid.extract_triangle_mesh(weight_threshold=1.5).to_legacy()
    mesh.compute_vertex_normals()
    return mesh, list(source.poses)


def made_up_wall(n=30, h=480, w=640):
    rng = np.random.default_rng(3)
    scale = 0.000125
    yy, xx = np.mgrid[0:h, 0:w]
    base = 0.40 + 0.00002 * (xx - w / 2)                       # a slightly angled wall, 40 cm away
    noise = np.full((h, w), 0.0006)
    noise[(xx - 470) ** 2 / 60 ** 2 + (yy - 150) ** 2 / 25 ** 2 < 1] = 0.004   # a scratch: flicker
    bias = np.zeros((h, w))
    bias[(xx - 200) ** 2 + (yy - 330) ** 2 < 40 ** 2] = 0.004  # a dent: reads steadily wrong
    hole = (xx - 320) ** 2 / 30 ** 2 + (yy - 240) ** 2 / 14 ** 2 < 1
    stack = []
    for _ in range(n):
        d = base + bias + rng.normal(0, 1, (h, w)) * noise
        d = (d / scale).astype(np.uint16)
        d[hole] = 0
        d[rng.random((h, w)) < 0.002] = 0
        stack.append(d)
    return np.array(stack), scale


root.geometry("+0+0")
pump(1.5)
print(GROUP, root.title())
if GROUP == "start":
    shot("main-window")
    scroll_panel(0.45)
    shot("detail-options")
elif GROUP == "plain":
    shot("plain-look")
elif GROUP == "mesh":
    mesh, poses = made_up_scan()
    preview = mesh.simplify_quadric_decimation(A.PREVIEW_MAX_TRIANGLES)
    app.msg_queue.put(("mesh_done", (o3d.geometry.PointCloud(mesh.vertices), mesh,
                                     A._mesh_to_arrays(preview) + (None,), "made-up scan.",
                                     (A.scan_view_direction(poses), A.scan_axes(poses)))))
    pump(1.5)
    app.preview.yaw, app.preview.pitch, app.preview.zoom = 0.55, 0.38, 1.5
    app.colour_mode_var.set(next(name for name, code in A.COLOUR_MODES if code == "height"))
    app._colour_mode_changed()
    pump(0.6)
    shot("colour-height")
    app.colour_mode_var.set(A.COLOUR_MODES[0][0])
    app._colour_mode_changed()
    scroll_panel(1.0)
    find_table = next(w for w in app.edit_widgets if str(w.cget("text")).startswith("Find the table"))
    find_table.invoke()
    pump(0.8)
    shot("cut-on-model")
elif GROUP == "turntable":
    app.scan_mode_var.set(dict((k, l) for l, k in A.SCAN_MODES)["rotary"])
    app._scan_mode_changed()
    pump(0.5)
    scan_frame = app.capture_btn.master
    scroll_panel(max(0.0, scan_frame.winfo_y() / max(1, app._side_panel.winfo_height()) - 0.01))
    shot("turntable-mode")
elif GROUP == "record":
    app.settings["pc_speed_ms"] = 130.0
    app.scan_style_var.set(dict((k, l) for l, k in A.SCAN_STYLES)["record"])
    app._scan_style_changed()
    pump(0.4)
    scan_frame = app.capture_btn.master
    scroll_panel(max(0.0, scan_frame.winfo_y() / max(1, app._side_panel.winfo_height()) + 0.03))
    shot("record-style")
elif GROUP == "dialogs":
    stack, scale = made_up_wall()
    app.camera.device_info = "Intel RealSense SR305 (S/N 000000000000) [made-up test wall]"
    app.camera.serial = "000000000000"
    result = A.analyze_wall(stack, scale)
    context = dict(camera=app.camera.device_info, laser=app.laser_var.get(), laser_mode="max",
                   confidence=app.confidence_var.get())
    app._show_health_window(result, context)
    pump(0.6)
    window = app.health_window
    window.geometry("+10+10")
    pump(0.8)
    shot("sensor-check", window)
    window.destroy()
pump(0.2)
app.on_close()
