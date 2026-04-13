#!/usr/bin/env python3
"""Render generated planes as 2D images from multiple views"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import trimesh
import numpy as np
import glob
import os

def render_multi_view(ply_path, output_path=None):
    """Render a PLY mesh from multiple views"""

    mesh = trimesh.load(ply_path)
    points, _ = trimesh.sample.sample_surface(mesh, 3000)

    fig = plt.figure(figsize=(15, 5))

    # 3D view
    ax1 = fig.add_subplot(141, projection='3d')
    ax1.scatter(points[:, 0], points[:, 1], points[:, 2],
                c=points[:, 2], cmap='plasma', s=1, alpha=0.8)
    ax1.set_title('3D View')
    ax1.set_xlabel('X'); ax1.set_ylabel('Y'); ax1.set_zlabel('Z')

    # Top view (X-Y plane)
    ax2 = fig.add_subplot(142)
    ax2.scatter(points[:, 0], points[:, 1], c=points[:, 2], cmap='plasma', s=1, alpha=0.8)
    ax2.set_title('Top View (X-Y)')
    ax2.set_aspect('equal')
    ax2.set_xlabel('X'); ax2.set_ylabel('Y')

    # Front view (X-Z plane)
    ax3 = fig.add_subplot(143)
    ax3.scatter(points[:, 0], points[:, 2], c=points[:, 2], cmap='plasma', s=1, alpha=0.8)
    ax3.set_title('Front View (X-Z)')
    ax3.set_aspect('equal')
    ax3.set_xlabel('X'); ax3.set_ylabel('Z')

    # Side view (Y-Z plane)
    ax4 = fig.add_subplot(144)
    ax4.scatter(points[:, 1], points[:, 2], c=points[:, 2], cmap='plasma', s=1, alpha=0.8)
    ax4.set_title('Side View (Y-Z)')
    ax4.set_aspect('equal')
    ax4.set_xlabel('Y'); ax4.set_ylabel('Z')

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150)
        print(f'Saved {output_path}')
    else:
        plt.savefig(ply_path.replace('.ply', '_render.png'), dpi=150)
        print(f'Saved {ply_path.replace(".ply", "_render.png")}')

def render_all_planes():
    """Render all generated planes"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gen_dir = os.path.join(base_dir, 'generated', 'GeneratedPlanes')
    output_dir = os.path.join(base_dir, 'images', 'renders')
    os.makedirs(output_dir, exist_ok=True)

    gen_files = sorted(glob.glob(os.path.join(gen_dir, '*.ply')))

    for f in gen_files:
        basename = os.path.basename(f).replace('.ply', '')
        output_path = os.path.join(output_dir, f'{basename}_render.png')
        render_multi_view(f, output_path)

    # Also create a comparison grid
    create_comparison_grid(gen_files, output_dir)

    print(f'\nAll renders saved to {output_dir}/')

def create_comparison_grid(files, output_dir):
    """Create a grid showing all planes"""
    n = len(files)
    fig = plt.figure(figsize=(5 * n, 10))

    for i, f in enumerate(files):
        mesh = trimesh.load(f)
        points, _ = trimesh.sample.sample_surface(mesh, 1500)

        ax = fig.add_subplot(2, n, i + 1)
        ax.scatter(points[:, 0], points[:, 1], c=points[:, 2], cmap='plasma', s=1, alpha=0.8)
        ax.set_title(f'Plane {i+1} - Top')
        ax.set_aspect('equal')
        ax.axis('off')

        ax2 = fig.add_subplot(2, n, i + 1 + n, projection='3d')
        ax2.scatter(points[:, 0], points[:, 1], points[:, 2], c=points[:, 2], cmap='plasma', s=1, alpha=0.8)
        ax2.set_title(f'Plane {i+1} - 3D')
        ax2.axis('off')

    plt.tight_layout()
    output_path = os.path.join(output_dir, 'all_planes_comparison.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f'Saved comparison grid: {output_path}')

if __name__ == "__main__":
    render_all_planes()
