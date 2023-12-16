import plyfile
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def read_ply(file_path):
    plydata = plyfile.PlyData.read(file_path)
    vertices = plydata['vertex'].data

    x = vertices['x']
    y = vertices['y']
    z = vertices['z']

    return x, y, z

def visualize_ply(x, y, z):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, marker='o', s=1)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.show()

if __name__ == "__main__":
    file_path = "airplane.ply"  # Substitua pelo caminho do seu arquivo PLY
    x, y, z = read_ply(file_path)
    visualize_ply(x, y, z)
