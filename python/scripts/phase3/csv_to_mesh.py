#!/usr/bin/env python3
"""
Convert soft_mesh.csv & hard_mesh.csv → .mesh files for Phase 3 FreeFEM simulations.
Auto-generates dummy CSVs if missing.
Generates valid triangle meshes for FreeFEM.
"""

import csv
import os
import sys

# Input CSV folder (mounted data folder)
data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data"))
os.makedirs(data_dir, exist_ok=True)

# CSV & mesh file paths
soft_csv = os.path.join(data_dir, "soft_mesh.csv")
hard_csv = os.path.join(data_dir, "hard_mesh.csv")
soft_mesh_file = os.path.join(data_dir, "soft_mesh.mesh")
hard_mesh_file = os.path.join(data_dir, "hard_mesh.mesh")

# Auto-create dummy CSVs if missing (simple triangle)
for csv_file in [soft_csv, hard_csv]:
    if not os.path.exists(csv_file):
        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["node_x","node_y","value"])
            writer.writerow([0,0,0])
            writer.writerow([1,0,1])
            writer.writerow([0,1,1])
        print(f"⚠️ {csv_file} missing, dummy CSV created with 3 nodes (triangle)")

def csv_to_mesh(csv_file, mesh_file):
    with open(csv_file, newline="") as f:
        reader = csv.DictReader(f)
        nodes = [ (float(row["node_x"]), float(row["node_y"])) for row in reader ]

    n = len(nodes)
    if n < 3:
        print(f"❌ ERROR: {csv_file} has only {n} nodes, need at least 3 for a valid mesh")
        sys.exit(1)

    # Write FreeFEM .mesh file
    with open(mesh_file, "w") as f:
        f.write("MeshVersionFormatted 2\n\n")

        # Vertices
        f.write("Vertices\n")
        f.write(f"{n}\n")
        for x, y in nodes:
            f.write(f"{x} {y} 0\n")  # boundary marker = 0

        # Triangles: simple fan around vertex 1
        f.write("\nTriangles\n")
        f.write(f"{n-2}\n")
        for i in range(2, n):
            f.write(f"1 {i} {i+1} 0\n")  # indices are 1-based, region marker = 0

        # Boundary edges
        f.write("\nEdges\n")
        f.write(f"{n}\n")
        for i in range(1, n):
            f.write(f"{i} {i+1} 1\n")  # boundary marker = 1
        f.write(f"{n} 1 1\n")  # close loop

        f.write("\nEnd\n")

    print(f"✅ Converted {csv_file} → {mesh_file} ({n} vertices, {n-2} triangles)")

# Convert both meshes
csv_to_mesh(soft_csv, soft_mesh_file)
csv_to_mesh(hard_csv, hard_mesh_file)
