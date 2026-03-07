from __future__ import annotations

from contextlib import AbstractContextManager


class ViewerSession(AbstractContextManager):
    def __init__(self, mesh=None, *, width=960, height=540, title="ThreeDimensions Viewer"):
        self.mesh = mesh
        self.width = int(width)
        self.height = int(height)
        self.title = title
        self.window = None
        self._yaw = 0.6
        self._pitch = 0.5
        self._zoom = 3.0
        self._dragging = False
        self._last = (0.0, 0.0)
        self._ran = False

    def _require(self):
        import glfw  # noqa: F401
        from OpenGL import GL  # noqa: F401
        from OpenGL import GLU  # noqa: F401

    def update(self, mesh):
        self.mesh = mesh

    def _init_window(self):
        self._require()
        import glfw

        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW")
        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Failed to create GLFW window")
        glfw.make_context_current(self.window)

        def _mouse_button(win, button, action, mods):
            if button == glfw.MOUSE_BUTTON_LEFT:
                self._dragging = action == glfw.PRESS

        def _cursor_pos(win, x, y):
            if self._dragging:
                dx = x - self._last[0]
                dy = y - self._last[1]
                self._yaw += dx * 0.005
                self._pitch = max(-1.5, min(1.5, self._pitch + dy * 0.005))
            self._last = (x, y)

        def _scroll(win, xo, yo):
            self._zoom = max(0.2, self._zoom - yo * 0.2)

        glfw.set_mouse_button_callback(self.window, _mouse_button)
        glfw.set_cursor_pos_callback(self.window, _cursor_pos)
        glfw.set_scroll_callback(self.window, _scroll)

    def _draw_mesh(self):
        if self.mesh is None:
            return
        from OpenGL import GL

        verts = self.mesh.vertices
        faces = self.mesh.faces

        GL.glColor3f(0.75, 0.79, 0.86)
        GL.glBegin(GL.GL_TRIANGLES)
        for face in faces:
            idx = list(face.indices) if hasattr(face, "indices") else list(face)
            if len(idx) < 3:
                continue
            v0 = verts[idx[0]]
            p0 = v0.position if hasattr(v0, "position") else v0
            for i in range(1, len(idx) - 1):
                va = verts[idx[i]]
                vb = verts[idx[i + 1]]
                pa = va.position if hasattr(va, "position") else va
                pb = vb.position if hasattr(vb, "position") else vb
                GL.glVertex3f(p0.x, p0.y, p0.z)
                GL.glVertex3f(pa.x, pa.y, pa.z)
                GL.glVertex3f(pb.x, pb.y, pb.z)
        GL.glEnd()

        GL.glColor3f(0.1, 0.1, 0.12)
        GL.glBegin(GL.GL_LINES)
        for face in faces:
            idx = list(face.indices) if hasattr(face, "indices") else list(face)
            for i in range(len(idx)):
                a = verts[idx[i]]
                b = verts[idx[(i + 1) % len(idx)]]
                pa = a.position if hasattr(a, "position") else a
                pb = b.position if hasattr(b, "position") else b
                GL.glVertex3f(pa.x, pa.y, pa.z)
                GL.glVertex3f(pb.x, pb.y, pb.z)
        GL.glEnd()

    def run(self):
        import glfw
        from OpenGL import GL, GLU

        if self.window is None:
            self._init_window()

        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glClearColor(0.07, 0.08, 0.1, 1.0)

        self._ran = True
        while not glfw.window_should_close(self.window):
            GL.glViewport(0, 0, self.width, self.height)
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            GL.glMatrixMode(GL.GL_PROJECTION)
            GL.glLoadIdentity()
            GLU.gluPerspective(55.0, self.width / float(max(1, self.height)), 0.01, 1000.0)

            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glLoadIdentity()
            cx = self._zoom * __import__("math").cos(self._pitch) * __import__("math").sin(self._yaw)
            cy = self._zoom * __import__("math").sin(self._pitch)
            cz = self._zoom * __import__("math").cos(self._pitch) * __import__("math").cos(self._yaw)
            GLU.gluLookAt(cx, cy, cz, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

            self._draw_mesh()

            glfw.swap_buffers(self.window)
            glfw.poll_events()

    def close(self):
        if self.window is not None:
            import glfw

            glfw.destroy_window(self.window)
            glfw.terminate()
            self.window = None

    def __enter__(self):
        self._init_window()
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.mesh is not None and not self._ran and exc_type is None:
            self.run()
        self.close()
        return False


def viewer(mesh=None, *, width: int = 960, height: int = 540, title: str = "ThreeDimensions Viewer"):
    """Use either `td.viewer(mesh)` for blocking preview or `with td.viewer() as scene:`."""
    session = ViewerSession(mesh=mesh, width=width, height=height, title=title)
    if mesh is not None:
        try:
            session.run()
        finally:
            session.close()
        return session
    return session
