import matplotlib.pyplot as plt
import numpy as np
import os
import subprocess
import glob
from matplotlib.colors import ListedColormap
from collections import defaultdict

class VideoGenerator:
    def __init__(self, name, colour_scheme={0: (0,0,0)}, output_folder="visualisations"):
        self.name = name
        self.output_folder = output_folder
        self.frame_folder = "frames"
        self.frame_count = 1
        
        # Normalize RGB colors to values between 0 and 1
        self.colour_scheme = {}
        for colour, tup in colour_scheme.items():
            if isinstance(tup, tuple):
                # Convert RGB values from 0-255 to 0-1 range
                self.colour_scheme[colour] = tuple(v / 255 for v in tup)
            else:
                self.colour_scheme[colour] = tup
                
        self.n_colours = len(self.colour_scheme)
        self.cmap = self.create_colormap()
        
        # Create necessary directories
        os.makedirs(f"{self.output_folder}", exist_ok=True)
        os.makedirs(f"{self.output_folder}/{self.name}", exist_ok=True)
        os.makedirs(f"{self.output_folder}/{self.name}/{self.frame_folder}", exist_ok=True)
        
        # Clear existing frames
        self.clear_frame_folder()
        
        # Generate the color palette
        self.generate_palette()

    def clear_frame_folder(self):
        """Removes all files in the frame folder."""
        frame_path = f"{self.output_folder}/{self.name}/{self.frame_folder}"
        for file_name in glob.glob(f"{frame_path}/*.png"):
            os.remove(file_name)
            
    def create_colormap(self):
        """Creates a ListedColormap from the color dictionary."""
        max_index = max(self.colour_scheme.keys())
        colors = []
        for i in range(max_index + 1):
            colors.append(self.colour_scheme.get(i, (0, 0, 0)))
        return ListedColormap(colors)
            
    def generate_palette(self):
        """Generates a palette visualization for the color map."""
        grid = np.array([[i for i in range(self.n_colours)]])
        plt.figure(figsize=(2, 0.5))
        plt.imshow(grid, cmap=self.cmap)
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.savefig(f"{self.output_folder}/{self.name}/generated_palette.png", 
                   bbox_inches='tight', pad_inches=0)
        plt.close()
        
    def draw_frame(self, frame):
        """Renders a 2D grid as an image using the current colormap."""
        frame = [[self.cmap(cell) for cell in row] for row in frame]
        npframe = np.array(frame)  # Remove dtype conversion
        plt.figure(figsize=(8, 8))
        plt.axis('off')
        plt.imshow(npframe)
       # plt.show()
        
    def draw_line(self, x, y, colour='red', linestyle="dashed", marker='o'):
        """Draws a line on the current frame."""
        plt.plot(x, y, color=colour, marker=marker, linestyle=linestyle)
        
    def print_frame(self):
        """Saves the current frame as an image."""
        plt.tight_layout(pad=0)
        plt.savefig(
            f"{self.output_folder}/{self.name}/{self.frame_folder}/{self.frame_count:09d}.png",
            bbox_inches='tight',
            pad_inches=0
        )
        self.frame_count += 1
        plt.close()
        
    def print_video(self, framerate=10,clear_frames=True):
        """Generates a video (GIF) from the saved frames."""
        # Generate palette for GIF
        subprocess.call([
            'ffmpeg',
            '-y',  # Overwrite existing files
            '-i', f'{self.output_folder}/{self.name}/generated_palette.png',
            '-vf', 'palettegen',
            f'{self.output_folder}/{self.name}/palette.png'
        ])
        
        # Create GIF using the palette
        subprocess.call([
            'ffmpeg',
            '-y',  # Overwrite existing files
            '-framerate', str(framerate),
            '-i', f'{self.output_folder}/{self.name}/{self.frame_folder}/%09d.png',
            '-i', f'{self.output_folder}/{self.name}/palette.png',
            '-filter_complex', 'paletteuse',
            f'{self.output_folder}/{self.name}/{self.name}.gif'
        ])
        # delete all images in the frames folder
        if clear_frames:
            self.clear_frame_folder()

# Example usage
if __name__ == "__main__":
    # Create a video generator with a color scheme
    vg = VideoGenerator("test", {
        0: (255, 255, 255),  # White
        1: (255, 0, 0),      # Red
        2: (0, 255, 0),      # Green
        3: (0, 0, 255),      # Blue
    })

    # Create test animation
    size = 3
    data = [[0 for _ in range(size)] for _ in range(size)]
    
    # Generate some frames
    for color in range(4):
        data[size//2][size//2] = color
        vg.draw_frame(data)
        vg.print_frame()

    # Create the final GIF
    vg.print_video(framerate=4)