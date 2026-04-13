#!/usr/bin/env python3
"""Visualize DeepSDF reconstruction results"""

import trimesh
import numpy as np
import os
import glob

def visualize_mesh(mesh_path, title="Mesh"):
    """Display mesh info"""
    mesh = trimesh.load(mesh_path)
    print(f"{title}:")
    print(f"  Vertices: {mesh.vertices.shape[0]}")
    print(f"  Faces: {mesh.faces.shape[0] if hasattr(mesh, 'faces') else 'N/A'}")
    print(f"  Bounds: {mesh.bounds}")
    print(f"  Is watertight: {mesh.is_watertight if hasattr(mesh, 'is_watertight') else 'N/A'}")
    return mesh

def compare_meshes(mesh1_path, mesh2_path, titles=None):
    """Compare two meshes side by side"""
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    if titles is None:
        titles = ["Mesh 1", "Mesh 2"]

    mesh1 = trimesh.load(mesh1_path)
    mesh2 = trimesh.load(mesh2_path)

    fig = plt.figure(figsize=(12, 5))

    ax1 = fig.add_subplot(121, projection='3d')
    ax1.scatter(mesh1.vertices[:, 0], mesh1.vertices[:, 1], mesh1.vertices[:, 2],
                c=mesh1.vertices[:, 2], cmap='viridis', s=0.5, alpha=0.5)
    ax1.set_title(titles[0])

    ax2 = fig.add_subplot(122, projection='3d')
    ax2.scatter(mesh2.vertices[:, 0], mesh2.vertices[:, 1], mesh2.vertices[:, 2],
                c=mesh2.vertices[:, 2], cmap='viridis', s=0.5, alpha=0.5)
    ax2.set_title(titles[1])

    plt.tight_layout()
    plt.show()

def show_random_samples(mesh_dir, n=5):
    """Show random samples from a directory"""
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    files = glob.glob(os.path.join(mesh_dir, "*.ply"))
    if len(files) == 0:
        print("No .ply files found")
        return

    indices = np.random.choice(len(files), min(n, len(files)), replace=False)

    fig = plt.figure(figsize=(15, 3 * n))

    for i, idx in enumerate(indices):
        mesh_path = files[idx]
        mesh = trimesh.load(mesh_path)

        # Sample points from the mesh surface
        points, _ = trimesh.sample.sample_surface(mesh, 2000)

        ax = fig.add_subplot(n, 3, i * 3 + 1, projection='3d')
        ax.scatter(points[:, 0], points[:, 1], points[:, 2],
                   c=points[:, 2], cmap='plasma', s=1, alpha=0.8)
        ax.set_title(f"{os.path.basename(mesh_path)[:20]}\n({points.shape[0]} points)")
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        # Top view
        ax2 = fig.add_subplot(n, 3, i * 3 + 2)
        ax2.scatter(points[:, 0], points[:, 1], c=points[:, 2], cmap='plasma', s=1, alpha=0.8)
        ax2.set_title('Top view (XY)')
        ax2.set_aspect('equal')

        # Side view
        ax3 = fig.add_subplot(n, 3, i * 3 + 3)
        ax3.scatter(points[:, 0], points[:, 2], c=points[:, 2], cmap='plasma', s=1, alpha=0.8)
        ax3.set_title('Side view (XZ)')
        ax3.set_aspect('equal')

    plt.tight_layout()
    plt.savefig('sample_planes.png', dpi=150)
    print(f"Saved visualization to sample_planes.png")
    plt.show()

if __name__ == "__main__":
    import sys
    import os

    # Default mesh directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mesh_dir = os.path.join(base_dir, 'data', 'Reconstructions', '600', 'Meshes', 'ShapeNetV2', '02691156')

    if len(sys.argv) > 1:
        if sys.argv[1] == "compare" and len(sys.argv) > 3:
            compare_meshes(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == "single" and len(sys.argv) > 2:
            visualize_mesh(sys.argv[2])
        else:
            show_random_samples(mesh_dir)
    else:
        show_random_samples(mesh_dir, n=6)
