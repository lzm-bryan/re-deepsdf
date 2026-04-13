#!/usr/bin/env python3
"""Generate comparison visualization: Generated vs Real latent reconstruction"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import trimesh
import numpy as np
import glob
import os

def visualize_generated_vs_real():
    """Compare generated planes with real reconstruction from test set"""

    # Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gen_dir = os.path.join(base_dir, 'generated', 'GeneratedPlanes')
    recon_dir = os.path.join(base_dir, 'data', 'Reconstructions', '600', 'Meshes', 'ShapeNetV2', '02691156')
    output_path = os.path.join(base_dir, 'images', 'generated_vs_real.png')

    # Get files
    gen_files = sorted(glob.glob(os.path.join(gen_dir, '*.ply')))
    recon_files = sorted(glob.glob(os.path.join(recon_dir, '*.ply')))

    if len(gen_files) == 0:
        print("No generated files found")
        return
    if len(recon_files) == 0:
        print("No reconstruction files found")
        return

    # Load meshes
    gen_mesh = trimesh.load(gen_files[0])
    np.random.seed(42)
    real_mesh = trimesh.load(recon_files[np.random.randint(0, len(recon_files))])

    # Create figure
    fig = plt.figure(figsize=(12, 5))

    # Real reconstruction
    ax1 = fig.add_subplot(121, projection='3d')
    p1, _ = trimesh.sample.sample_surface(real_mesh, 2000)
    ax1.scatter(p1[:, 0], p1[:, 1], p1[:, 2], c=p1[:, 2], cmap='plasma', s=1, alpha=0.8)
    ax1.set_title(f'Real (Test Set Reconstruction)\n{len(real_mesh.vertices)} verts')
    ax1.set_xlabel('X'); ax1.set_ylabel('Y'); ax1.set_zlabel('Z')
    ax1.set_xlim([-1.5, 1.5]); ax1.set_ylim([-1.5, 1.5]); ax1.set_zlim([-1.5, 1.5])

    # Generated
    ax2 = fig.add_subplot(122, projection='3d')
    p2, _ = trimesh.sample.sample_surface(gen_mesh, 2000)
    ax2.scatter(p2[:, 0], p2[:, 1], p2[:, 2], c=p2[:, 2], cmap='plasma', s=1, alpha=0.8)
    ax2.set_title(f'Generated (Random Latent)\n{len(gen_mesh.vertices)} verts')
    ax2.set_xlabel('X'); ax2.set_ylabel('Y'); ax2.set_zlabel('Z')
    ax2.set_xlim([-1.5, 1.5]); ax2.set_ylim([-1.5, 1.5]); ax2.set_zlim([-1.5, 1.5])

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f'Saved {output_path}')

if __name__ == "__main__":
    visualize_generated_vs_real()
