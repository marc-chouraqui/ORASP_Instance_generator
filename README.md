# ORASP Instance Generator

This repository contains a Python script to generate benchmark instances for the **Operating Room Assignment and Surgical Planning (ORASP)** problem.

The instances reflect realistic hospital constraints such as surgeon schedules, room compatibility, operation durations, and inter-operation setup times.

---

## 📘 Model Overview

Each instance defines:
- **O**: set of operations
- **C**: set of surgeons
- **S**: set of operating rooms  
It includes:
- **A[o][s]**: compatibility matrix between operations and rooms
- **X[c][o]**: binary matrix indicating if surgeon c can perform operation o
- **F**, **G**: surgeon availability windows
- **TP**, **TC**, **TN**, **TT**: prep, surgery, cleaning, and total times per operation
- **T[o][t]**: type of each operation
- **TD[o1][o2]**: setup time between two operations in the same room
- **Tmax**, **M**: model constants

---

## ▶️ How to Use

```bash
pip install numpy
python generator.py
