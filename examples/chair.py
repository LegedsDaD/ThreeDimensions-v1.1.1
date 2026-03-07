import sys
import os
import math

# Force import from local source to pick up latest changes
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'python')))

import threedimensions as td

def create_chair():
    print("Creating a 3D Chair...")
    
    # 1. Create the Seat
    # A box for the seat: 40cm x 5cm x 40cm (0.4 x 0.05 x 0.4)
    # We create a cube of size 1 and scale it
    seat = td.Mesh.create_cube(size=1.0)
    seat.name = "Chair"
    seat.scale(0.4, 0.05, 0.4)
    seat.translate(0, 0.45, 0) # Lift it up (legs height ~0.45)
    
    # 2. Create Legs
    # Legs: 4cm x 4cm x 45cm (0.04 x 0.45 x 0.04)
    leg_size = 0.04
    leg_height = 0.45
    
    # We'll create one leg template
    leg_template = td.Mesh.create_cube(size=1.0)
    leg_template.scale(leg_size, leg_height, leg_size)
    # Move so its bottom is at 0 (cube center is at 0, so bottom is -height/2)
    # We want bottom at 0, so move up by height/2
    leg_template.translate(0, leg_height/2, 0)
    
    # Position offsets for 4 legs
    # Seat is 0.4 wide, centered at 0.
    # Corners are at +/- 0.2
    # Indent legs slightly: +/- 0.17
    offset = 0.17
    
    print("Adding Legs...")
    seat.join(leg_template, offset_x=offset,  offset_y=0, offset_z=offset)  # Front-Right
    seat.join(leg_template, offset_x=-offset, offset_y=0, offset_z=offset)  # Front-Left
    seat.join(leg_template, offset_x=offset,  offset_y=0, offset_z=-offset) # Back-Right
    seat.join(leg_template, offset_x=-offset, offset_y=0, offset_z=-offset) # Back-Left
    
    # 3. Create Backrest
    # Backrest Pillars
    # Extend the back legs up? Or add new geometry?
    # Let's add new geometry for simplicity.
    
    back_pillar = td.Mesh.create_cube(size=1.0)
    back_height = 0.5
    back_pillar.scale(leg_size, back_height, leg_size)
    # Position on top of seat (y=0.45 + 0.025 = 0.475 start?)
    # Center of pillar should be at 0.45 + back_height/2
    pillar_y = 0.45 + (back_height / 2)
    
    print("Adding Backrest...")
    # Add pillars
    seat.join(back_pillar, offset_x=offset,  offset_y=pillar_y, offset_z=-offset)
    seat.join(back_pillar, offset_x=-offset, offset_y=pillar_y, offset_z=-offset)
    
    # Backrest horizontal slats
    slat = td.Mesh.create_cube(size=1.0)
    # Width: distance between pillars + thickness = 2*offset + leg_size
    slat_width = (2 * offset) + leg_size
    slat_height = 0.1
    slat_thick = 0.02
    slat.scale(slat_width, slat_height, slat_thick)
    
    # Top slat
    seat.join(slat, offset_x=0, offset_y=0.45 + back_height - 0.05, offset_z=-offset)
    
    # Middle slat
    seat.join(slat, offset_x=0, offset_y=0.45 + back_height/2, offset_z=-offset)
    
    print(f"Chair generated: {seat.vertex_count} vertices, {seat.face_count} faces.")
    
    # Auto-save
    seat.save("chair.obj")
    print("Saved chair.obj")
    seat.save("chair.stl")
    print("Saved chair.stl")

if __name__ == "__main__":
    create_chair()
