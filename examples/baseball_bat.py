import sys
import os
import math

# Try to import from installed package first
try:
    import threedimensions as td
except ImportError:
    # Fallback to local source if not installed
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python'))
    import threedimensions as td

def create_baseball_bat():
    print("Creating Baseball Bat...")
    
    # 1. Start with the handle
    # A standard bat is about 34 inches (~0.86m).
    # Let's say handle diameter is ~2.5cm (0.025m), Barrel ~6.5cm (0.065m).
    # We'll work in generic units where 1.0 = 10cm for easier visualization.
    
    # Start with the handle part
    segments = 32
    bat = td.Mesh.create_cylinder(radius=0.15, height=1.0, segments=segments)
    bat.name = "Baseball Bat"
    
    # Cylinder faces:
    # 0 to segments-1: Side faces
    # segments: Bottom Cap
    # segments+1: Top Cap
    
    top_face_idx = bat.face_count - 1
    bottom_face_idx = bat.face_count - 2
    
    # === Form the Barrel (Extrude Up) ===
    
    # Transition from handle to barrel (taper)
    # Extrude 1: Start taper
    bat.extrude_face(top_face_idx, distance=0.5)
    bat.scale_face(top_face_idx, 1.2) # Slightly wider
    
    # Extrude 2: More taper
    bat.extrude_face(top_face_idx, distance=1.0)
    bat.scale_face(top_face_idx, 1.5) 
    
    # Extrude 3: Reach full barrel width
    bat.extrude_face(top_face_idx, distance=1.0)
    bat.scale_face(top_face_idx, 1.4) # Final widening to ~0.38 radius
    
    # Extrude 4: Main Barrel Length
    bat.extrude_face(top_face_idx, distance=4.0)
    
    # Extrude 5: Rounded Top (Cap)
    bat.extrude_face(top_face_idx, distance=0.1)
    bat.scale_face(top_face_idx, 0.8)
    
    bat.extrude_face(top_face_idx, distance=0.05)
    bat.scale_face(top_face_idx, 0.5)
    
    # === Form the Knob (Extrude Down) ===
    
    # Extrude bottom face down for the knob
    bat.extrude_face(bottom_face_idx, distance=0.1)
    bat.scale_face(bottom_face_idx, 1.5) # Widen for knob
    
    bat.extrude_face(bottom_face_idx, distance=0.05)
    bat.scale_face(bottom_face_idx, 0.8) # Round off bottom
    
    print(f"Bat generated: {bat.vertex_count} vertices, {bat.face_count} faces.")
    
    # Auto-save demonstration
    bat.save("baseball_bat.obj")
    print(f"Auto-saved bat to baseball_bat.obj")
    
    return bat

def main():
    bat = create_baseball_bat()

if __name__ == "__main__":
    main()
