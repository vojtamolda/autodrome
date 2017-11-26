import pyglet
from pyglet.gl import gl
from pyglet.gl import glu
import pywavefront
from pywavefront import visualization

from autodrome import ETS2, ATS


class Window(pyglet.window.Window):

    def __init__(self, simulator):
        pyglet.window.Window.__init__(self)
        self.simulator = simulator
        obj_file = simulator.mod_dir / 'map/indy500.obj'
        self.mesh = pywavefront.Wavefront(obj_file, create_materials=True)
        self.x, self.y, self.z = 0.0, 0.0, -220.0
        self.rx, self.ry, self.rz = 90.0, 0.0, 0.0
        self.data = None

        @self.event
        def on_resize(width, height):
            gl.glMatrixMode(gl.GL_PROJECTION)
            glu.gluPerspective(90, float(width)/height, 10, 1_000)
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            gl.glMatrixMode(gl.GL_MODELVIEW)
            return pyglet.event.EVENT_HANDLED

        @self.event
        def on_draw():
            window.clear()
            gl.glLoadIdentity()
            gl.glTranslated(self.x, self.y, self.z)
            gl.glRotatef(self.rx, 1, 0, 0)
            gl.glRotatef(self.ry, 0, 1, 0)
            gl.glRotatef(self.rz, 0, 0, 1)
            visualization.draw(self.mesh)
            # TODO: Add truck model to the scene

        @self.event
        def on_mouse_drag(x, y, dx, dy, button, modifiers):
            if button == pyglet.window.mouse.LEFT:
                self.x += dx
                self.y += dy
            if button == pyglet.window.mouse.RIGHT:
                self.ry += dx
                self.rx -= dy

        @self.event
        def on_mouse_scroll(x, y, scroll_x, scroll_y):
            self.z -= scroll_y

    def update(self, dt):
        if simulator.process.poll() is not None:
            self.close()
        reply = simulator.telemetry.wait(simulator.telemetry.Event.frameEnd, timeout=0.01)
        if reply:
            self.data = reply.data.telemetry
        if self.data:
            if self.data.wearCabin > 0 or self.data.wearChassis > 0:
                self.close()
        # TODO: Update truck model location


if __name__ == '__main__':
    # TODO: Add argparse options for ATS/ETS2 and map selection
    with ETS2() as simulator:
        simulator.command('preview indy500')
        simulator.wait()

        window = Window(simulator)
        pyglet.clock.schedule(window.update)
        pyglet.app.run()
