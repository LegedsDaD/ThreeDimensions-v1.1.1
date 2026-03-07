import sys
import os
import math

# Force import from local source to pick up latest changes
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'python')))

import threedimensions as td

def create_bed():
    print("Creating a 3D Bed...")
    
    # Bed dimensions (approximate)
    # Length: 2.0m, Width: 1.6m (Queen), Height: 0.5m
    
    bed_length = 2.0
    bed_width = 1.6
    bed_height = 0.5
    
    # 1. Create Mattress
    # Mattress is a box
    mattress = td.Mesh.create_cube(size=1.0)
    mattress.name = "Bed"
    mattress.scale(bed_width, 0.25, bed_length)
    mattress.translate(0, bed_height, 0) # Place top surface at ~0.6m
    
    # 2. Create Frame/Base
    frame = td.Mesh.create_cube(size=1.0)
    frame.scale(bed_width, 0.15, bed_length)
    # Position frame below mattress
    # Mattress center Y: 0.5
    # Frame center Y: 0.5 - 0.125 - 0.075 = 0.3
    # Actually let's just use relative offsets when joining
    
    # Join Frame to Mattress mesh (acting as the main object)
    # Frame is 0.2m below mattress center
    mattress.join(frame, offset_x=0, offset_y=-0.2, offset_z=0)
    
    # 3. Legs
    leg_size = 0.08
    leg_h = 0.3
    leg_template = td.Mesh.create_cube(size=1.0)
    leg_template.scale(leg_size, leg_h, leg_size)
    
    # Leg positions
    dx = (bed_width / 2) - 0.05
    dz = (bed_length / 2) - 0.05
    leg_y = -0.4 # Relative to mattress center (0.5) -> 0.1 (ground is at 0?)
    # If mattress center is 0.5, bottom is 0.375. 
    # Frame center 0.3, bottom 0.225.
    # Legs need to go from 0 to 0.225.
    # Let's adjust heights.
    
    # Resetting logic for cleaner composition:
    # Let's create a new root object for the bed to keep things clean
    bed = td.Mesh.create_cube(size=1.0) 
    # Hack: We want an empty mesh, but we don't have a clear() exposed easily in factory
    # So we'll make a tiny hidden cube or just use the mattress as base.
    # Using mattress as base.
    
    # Legs relative to mattress center (0.5)
    # They need to be at corners.
    # Y position: Mattress(0.5) -> Frame(0.3) -> Legs(center at 0.15, height 0.3)
    # Offset Y = 0.15 - 0.5 = -0.35
    
    mattress.join(leg_template, offset_x=dx, offset_y=-0.35, offset_z=dz)
    mattress.join(leg_template, offset_x=-dx, offset_y=-0.35, offset_z=dz)
    mattress.join(leg_template, offset_x=dx, offset_y=-0.35, offset_z=-dz)
    mattress.join(leg_template, offset_x=-dx, offset_y=-0.35, offset_z=-dz)
    
    # 4. Headboard
    # Large panel at the back
    headboard = td.Mesh.create_cube(size=1.0)
    hb_height = 1.0
    hb_thick = 0.1
    headboard.scale(bed_width, hb_height, hb_thick)
    
    # Position: Back of bed (-z), extending up
    # Z offset: -bed_length/2 - 0.05
    # Y offset: Center at say 0.5 (starts at 0, goes to 1.0)
    # Relative to mattress center (0.5): offset y = 0
    mattress.join(headboard, offset_x=0, offset_y=0.25, offset_z=-(bed_length/2 + 0.05))
    
    # 5. Pillows
    # Cylinders or scaled spheres
    pillow = td.Mesh.create_cube(size=1.0)
    pillow.scale(0.6, 0.15, 0.4)
    
    # Place on top of mattress
    # Mattress top is 0.5 + 0.125 = 0.625
    # Pillow center y = 0.625 + 0.075 = 0.7
    # Relative to mattress center (0.5): +0.2
    
    # Z position: Near headboard
    pz = -(bed_length/2) + 0.4
    px = bed_width / 4
    
    mattress.join(pillow, offset_x=px, offset_y=0.2, offset_z=pz)
    mattress.join(pillow, offset_x=-px, offset_y=0.2, offset_z=pz)
    
    print(f"Bed generated: {mattress.vertex_count} vertices, {mattress.face_count} faces.")
    
    # Auto-save
    mattress.save("bed.obj")
    print("Saved bed.obj")
    mattress.save("bed.stl")
    print("Saved bed.stl")

if __name__ == "__main__":
    create_bed()
