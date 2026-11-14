---
title: "Icy Ewe: 3D scanning on the cheap with a scratched depth camera and a slow laptop"
published: false
tags: 3dscanning, python, opensource, computervision
---

Second-hand depth cameras (an Intel RealSense SR305, the D415 hiding inside a Prowise MOVE 3in1) see depth 30 times a
second for the price of a takeaway. Turning one into a 3D scanner is easy right up to the point where you line the
frames up. Then the object grows a second nose.

I'm working on about 50 projects at once, so I don't have the time or brain capacity for humour; it cuts into my four
hours of sleep-eating time (efficiency). So, straight to it, apart from the title: **Icy Ewe** (say it out loud) is the write-up of how my app,
Scantastic, keeps a scan together on bad cameras and slow computers:

- **Picture features check every step** the 3D shape suggests, and veto it when the shape is fooling itself.
- **Loop closures can't lie:** one the pictures can't confirm may only move a frame as far as the chain could really
  have drifted. On a plain test blob, 40 of 42 closures had been wrong.
- **Turntable mode** holds every frame to one fitted axis; a printed marker ring is optional.
- **TRACKING LOST** tells you while you can still do something about it.
- **Slow PCs record now and stitch afterwards**, in a separate process that just tries again on fewer frames if it
  runs out of memory.
- **Speed profiles, side-by-side alignment with identical answers, and a graphics card that has to pass a test first.**
- **A sensor check** that maps where your camera's window is scratched.

The honest bit: all the measured results come from made-up scans with known answers, and the new methods haven't been
through a real camera yet. There's a test plan in section 8. If you have one of these cameras, please break it and tell
me what happened.

It's also a **defensive publication**: section 9 dedicates the methods and their variations to the public, so they stay
free for hobbyists.

Paper: https://github.com/The-Dorkknight/icy-ewe · App: https://github.com/The-Dorkknight/scantastic
