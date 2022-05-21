from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from PIL import Image
import numpy
import math
import sys

WINDOW_NAME = '3D Earth'

class Window_3DSpace:
    def __init__(self):
        self.angle = 0
        self.moon_angle = 0
        self.backg_id = 0
        self.earth_angle_increment = 1.5
        self.moon_angle_increment = 0.4
        self.scale_factor = 0
        self.VOID, self.START_MOTION, self.STOP_MOTION, self.RESET, self.QUIT = list(
            range(5))
        self.menudict = {self.START_MOTION: self.start_motion,
                         self.STOP_MOTION: self.stop_motion,
                         self.RESET: self.reset,
                         self.QUIT: self.close}

    def reset(self):
        self.earth_angle_increment = 1.5
        self.scale_factor = 0
        self.moon_angle_increment = 0.4

    def start_motion(self):
        self.earth_angle_increment = 1.5
        self.moon_angle_increment = 0.4

    def stop_motion(self):
        self.earth_angle_increment = 0
        self.moon_angle_increment = 0

    def close(self):
        glutDestroyWindow(glutGetWindow())
        return

    def dmenu(self, item):
        self.menudict[item]()
        return 0

    def key_input(self, char, y, z):
        if char == b'x':
            self.earth_angle_increment = 3 if self.earth_angle_increment == 0 else 0
        elif char == b'w':
            self.scale_factor += 0.1 if self.scale_factor < 2 else 0
        elif char == b's':
            self.scale_factor -= 0.1 if self.scale_factor > -0.5 else 0
        elif char == b'r':
            self.reset()

    def mouse_input(self, button, state, x, y):
        if button == 4:
            self.scale_factor -= 0.1 if self.scale_factor > -0.5 else 0
        elif button == 3:
            self.scale_factor += 0.1 if self.scale_factor < 2 else 0

    def get_texture(self, filename, pictype):
        img = Image.open(filename)
        img_data = numpy.array(list(img.getdata()), numpy.int8)
        if pictype == 'jpg':
            glActiveTexture(GL_TEXTURE1)
        else:
            glActiveTexture(GL_TEXTURE0)
        textID = glGenTextures(1)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glBindTexture(GL_TEXTURE_2D, textID)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
                     img.size[0], img.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
        img.close()
        return textID

    def setup_lighting(self):
        # lighting setup
        glEnable(GL_LIGHTING)
        glLightfv(GL_LIGHT0, GL_POSITION, [-10, 12, 8, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.05)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
        glEnable(GL_LIGHT0)

    def fetch_textures(self):
        self.backg_texture_id = self.get_texture(
            'assets/8k_stars_milky_way.jpg', 'jpg')
        self.sun_texture_id = self.get_texture('assets/8k_sun.jpg', 'jpg')
        self.earth_texture_id = self.get_texture('assets/8k_earth_daymap.jpg', 'jpg')
        self.moon_texture_id = self.get_texture('assets/2k_moon.png', 'png')

    def setup(self):
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(1200, 800)
        glutInitWindowPosition(800, 200)
        glutCreateWindow(WINDOW_NAME)
        glClearColor(0., 0., 0., 1.)
        glMatrixMode(GL_PROJECTION)
        gluPerspective(40, 1, 1, 20)
        glMatrixMode(GL_MODELVIEW)
        gluLookAt(0, 4, 0, 0, 0, 0, 0, 0, 1)
        self.setup_lighting()
        self.fetch_textures()

        glutDisplayFunc(self.draw)

        # setup mouse and keyboard controls
        glutKeyboardFunc(self.key_input)
        glutMouseFunc(self.mouse_input)
        self.setup_menu()
        glutMainLoop()


    def setup_menu(self):
        #setup menu to control motions
        glutCreateMenu(self.dmenu)
        glutAddMenuEntry("Start Motion", self.START_MOTION)
        glutAddMenuEntry("Stop Motion", self.STOP_MOTION)
        glutAddMenuEntry("Reset", self.RESET)
        glutAddMenuEntry("Quit", self.QUIT)
        glutAttachMenu(GLUT_RIGHT_BUTTON)

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0, 4, 0, 0, 0, 0, 0, 0, 1)
        glEnable(GL_DEPTH_TEST)
        self.render_earth()
        self.render_moon()
        self.render_sun()
        self.render_background()

        glutSwapBuffers()
        glutPostRedisplay()

    def render_earth(self):
        # earth
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.earth_texture_id)
        glPushMatrix()
        glEnable(GL_LIGHTING)
        glTranslatef(0.5 - self.scale_factor/5, 0.5 + self.scale_factor, 0)
        glScalef((glutGet(GLUT_WINDOW_HEIGHT)) /
                 (glutGet(GLUT_WINDOW_WIDTH)), 1, 1)
        glRotatef(self.angle, 0, 0, 1)
        self.angle += self.earth_angle_increment
        glScalef(1, 1, -1)  # sulto pareko
        qobj = gluNewQuadric()
        gluQuadricTexture(qobj, GL_TRUE)
        gluSphere(qobj, 0.5, 50, 50)
        glPopMatrix()
        gluDeleteQuadric(qobj)
        glDisable(GL_TEXTURE_2D)

    def render_moon(self):
        # moon
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.moon_texture_id)
        glTranslatef(0.5 - self.scale_factor/5, 0.5 + self.scale_factor, 0)
        glPushMatrix()
        glEnable(GL_LIGHTING)
        glScalef(glutGet(GLUT_WINDOW_HEIGHT)/glutGet(GLUT_WINDOW_WIDTH), 1, 1)
        glRotatef(self.moon_angle, 0, 0, 1)
        self.moon_angle += self.moon_angle_increment
        glTranslatef(1, 0, 0)
        sobj = gluNewQuadric()
        gluQuadricTexture(sobj, GL_TRUE)
        gluSphere(sobj, 0.125, 50, 50)
        glPopMatrix()
        gluDeleteQuadric(sobj)
        glDisable(GL_TEXTURE_2D)

    def render_sun(self):
        # sun
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.sun_texture_id)
        glPushMatrix()
        glDisable(GL_LIGHTING)
        glScalef(glutGet(GLUT_WINDOW_HEIGHT)/glutGet(GLUT_WINDOW_WIDTH), 1, 1)
        glTranslatef(-1.8, 2, 0.8)
        sobj = gluNewQuadric()
        gluQuadricTexture(sobj, GL_TRUE)
        gluSphere(sobj, 0.6, 50, 50)
        glPopMatrix()
        gluDeleteQuadric(sobj)
        glDisable(GL_TEXTURE_2D)

    def render_background(self):
        # background
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.backg_texture_id)
        glPushMatrix()
        glDisable(GL_LIGHTING)
        glScalef(glutGet(GLUT_WINDOW_HEIGHT)/glutGet(GLUT_WINDOW_WIDTH), 1, 1)
        glTranslatef(0, -10, 0)
        sobj = gluNewQuadric()
        gluQuadricTexture(sobj, GL_TRUE)
        gluSphere(sobj, 8, 50, 50)
        glPopMatrix()
        gluDeleteQuadric(sobj)
        glDisable(GL_TEXTURE_2D)

    


if __name__ == "__main__":
    w = Window_3DSpace()
    w.setup()
    glutMainLoop()
