from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse
from Model import Model
import sys

from Constants import *

import time

class Window(pyglet.window.Window):

    def __init__(self, line = None, col = None, bomb = None, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.lines = line
        self.columns = col

        self.is_losse = False

        self.is_win = False

        # Whether or not the window exclusively captures the mouse.
        self.exclusive = False

        # When flying gravity has no effect and speed is increased.
        self.flying = False

        # Used for constant jumping. If the space bar is held down,
        # this is true, otherwise, it's false
        self.jumping = False

        # If the player actually jumped, this is true
        self.jumped = False

        # If this is true, a crouch offset is added to the final glTranslate
        self.crouch = False

        # Player sprint
        self.sprinting = False

        # This is an offset value so stuff like speed potions can also be easily added
        self.fov_offset = 0

        self.collision_types = {"top": False, "bottom": False, "right": False, "left": False}

        # Strafing is moving lateral to the direction you are facing,
        # e.g. moving to the left or right while continuing to face forward.
        #
        # First element is -1 when moving forward, 1 when moving back, and 0
        # otherwise. The second element is -1 when moving left, 1 when moving
        # right, and 0 otherwise.
        self.strafe = [0, 0]

        # Current (x, y, z) position in the world, specified with floats. Note
        # that, perhaps unlike in math class, the y-axis is the vertical axis.
        self.position = (0, 20, 0)

        # First element is rotation of the player in the x-z plane (ground
        # plane) measured from the z-axis down. The second is the rotation
        # angle from the ground plane up. Rotation is in degrees.
        #
        # The vertical plane rotation ranges from -90 (looking straight down) to
        # 90 (looking straight up). The horizontal rotation range is unbounded.
        self.rotation = (0, 0)

        # Which sector the player is currently in.
        self.sector = None

        # The crosshairs at the center of the screen.
        self.reticle = None

        # Velocity in the y (upward) direction.
        self.dy = 0

        # A list of blocks the platoyer can place. Hit num keys to cycle.
        self.inventory = [RESET]
        # The current block the user can place. Hit num keys to cycle.
        #self.block = self.inventory[0]

        # Convenience list of num keys.
        self.num_keys = [
            key._1, key._2, key._3, key._4, key._5,
            key._6, key._7, key._8, key._9, key._0]

        # Instance of the model that handles the world.
        self.model = Model(line, col, bomb)

        # The label that is displayed in the top left of the canvas.
        self.label = pyglet.text.Label('', font_name='Arial', font_size=18,
            x=10, y=self.height - 10, anchor_x='left', anchor_y='top',
            color=(0, 0, 0, 255))

        self.game_status = pyglet.text.Label('', font_name='Arial', font_size=30,
            x=self.width//2, y=self.height//2, anchor_x='center', anchor_y='center',
            color=(250, 50, 35, 255))

        # This call schedules the `update()` method to be called
        # TICKS_PER_SEC. This is the main game event loop.
        pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SEC)

    def set_exclusive_mouse(self, exclusive):
        """ If `exclusive` is True, the game will capture the mouse, if False
        the game will ignore the mouse.
        """
        super(Window, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive

    def get_sight_vector(self):
        """ Returns the current line of sight vector indicating the direction
        the player is looking.
        """
        x, y = self.rotation
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return (dx, dy, dz)

    def get_motion_vector(self):
        """ Returns the current motion vector indicating the velocity of the
        player.

        Returns
        -------
        vector : tuple of len 3
            Tuple containing the velocity in x, y, and z respectively.

        """
        if any(self.strafe):
            x, y = self.rotation
            strafe = math.degrees(math.atan2(*self.strafe))
            y_angle = math.radians(y)
            x_angle = math.radians(x + strafe)
            if self.flying:
                m = math.cos(y_angle)
                dy = math.sin(y_angle)
                if self.strafe[1]:
                    # Moving left or right.
                    dy = 0.0
                    m = 1
                if self.strafe[0] > 0:
                    # Moving backwards.
                    dy *= -1
                # When you are flying up or down, you have less left and right
                # motion.
                dx = math.cos(x_angle) * m
                dz = math.sin(x_angle) * m
            else:
                dy = 0.0
                dx = math.cos(x_angle)
                dz = math.sin(x_angle)
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return (dx, dy, dz)

    def update(self, dt):
        """ This method is scheduled to be called repeatedly by the pyglet
        clock.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        self.model.process_queue()
        sector = sectorize(self.position)
        if sector != self.sector:
            self.model.change_sectors(self.sector, sector)
            if self.sector is None:
                self.model.process_entire_queue()
            self.sector = sector
        m = 8
        dt = min(dt, 0.2)
        for _ in xrange(m):
            self._update(dt / m)

    def _update(self, dt):
        """ Private implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        # walking
        if self.flying:
            speed = FLYING_SPEED
        elif self.sprinting:
            speed = SPRINT_SPEED
        elif self.crouch:
            speed = CROUCH_SPEED
        else:
            speed = WALKING_SPEED

        if self.jumping:
            self.dy = JUMP_SPEED

        if self.jumped:
            speed += 0.7

        d = dt * speed # distance covered this tick.
        dx, dy, dz = self.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d
        # gravity
            # Update your vertical speed: if you are falling, speed up until you
            # hit terminal velocity; if you are jumping, slow down until you
            # start falling.
        if self.crouch:
            self.dy = - 50
        if not self.flying:
            self.dy -= dt * GRAVITY
            self.dy = max(self.dy, -TERMINAL_VELOCITY)
        elif self.jumping and self.flying: 
            self.dy = 17
        elif self.flying:
            self.dy = 0
        dy += self.dy * dt
        # collisions
        old_pos = self.position
        x, y, z = old_pos
        x, y, z = self.collide((x + dx, y + dy, z + dz), PLAYER_HEIGHT)
        self.position = (x, y, z)

        if self.collision_types["top"]:
            self.jumped = False

        # Sptinting stuff. If the player stops moving in the x and z direction, the player stops sprinting
        # and the sprint fov is subtracted from the fov offset
        if old_pos[0]-self.position[0] == 0 and old_pos[2]-self.position[2] == 0:
            disablefov = False
            if self.sprinting:
                disablefov = True
            self.sprinting = False
            if disablefov:
                self.fov_offset -= SPRINT_FOV

    def collide(self, position, height):
        """ Checks to see if the player at the given `position` and `height`
        is colliding with any blocks in the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check for collisions at.
        height : int or float
            The height of the player.

        Returns
        -------
        position : tuple of len 3
            The new position of the player taking into account collisions.

        """
        # How much overlap with a dimension of a surrounding block you need to
        # have to count as a collision. If 0, touching terrain at all counts as
        # a collision. If .49, you sink into the ground, as if walking through
        # tall grass. If >= .5, you'll fall through the ground.
        pad = 0.25
        p = list(position)
        np = normalize(position)
        self.collision_types = {"top":False,"bottom":False,"right":False,"left":False}
        for face in FACES:  # check all surrounding blocks
            for i in xrange(3):  # check each dimension independently
                if not face[i]:
                    continue
                # How much overlap you have with this dimension.
                d = (p[i] - np[i]) * face[i]
                if d < pad:
                    continue
                for dy in xrange(height):  # check each height
                    op = list(np)
                    op[1] -= dy
                    op[i] += face[i]
                    if tuple(op) not in self.model.world:
                        continue
                    p[i] -= (d - pad) * face[i]
                    # If you are colliding with the ground or ceiling, stop
                    # falling / rising.
                    if face == (0, -1, 0):
                        self.collision_types["top"] = True
                        self.dy = 0
                    if face == (0, 1, 0):
                        self.collision_types["bottom"] = True
                        self.dy = 0
                    break
        return tuple(p)

    def convert_block_to_2D_position(self, block):
        x, y, z = block
        return x, z

    def set_reset(self):
        center_x, center_z = self.model.get_grid_center()
        for y in range(1, 4):
            if self.is_losse or self.is_win:
                self.model.add_block((center_x, y, center_z), RESET, immediate = True)

            else:
                self.model.remove_block((center_x, y, center_z))
                #display_bomb()

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called when a mouse button is pressed. See pyglet docs for button
        amd modifier mappings.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        button : int
            Number representing mouse button that was clicked. 1 = left button,
            4 = right button.
        modifiers : int
            Number representing any modifying keys that were pressed when the
            mouse button was clicked.

        """
        if self.exclusive:
            vector = self.get_sight_vector()
            block, previous = self.model.hit_test(self.position, vector)
            print(str(block))
            if(self.model.world[block] == RESET):
                self.is_losse = False
                self.is_win = False
                self.set_reset()
                self.model.gen_demineur(True, self.is_win)
                return

            if not self.is_losse and block[1] == 0:
                cell = self.model.grid[block[0]][block[2]]
                if (button == mouse.RIGHT) :
                    # ON OSX, control + left click = right click.
                    if cell.state != cell._REVEALED and not cell.flagged:
                        if cell.is_bomb:
                            self.model.display_bombs()
                            self.is_losse = True
                            self.set_reset()
                        else:
                            self.model.reveal(cell, block)
                elif (button == mouse.LEFT) and (modifiers & key.MOD_CTRL):
                    cell.flagged = not cell.flagged
                    if cell.flagged:
                        self.model.add_block(block, FLAG)
                    else:
                        self.model.add_block(block, HIDED_CELL)
            '''elif button == pyglet.window.mouse.LEFT and block:
                texture = self.model.world[block]
                self.model.remove_block(block)'''
        else:
            self.set_exclusive_mouse(True)
        if self.model.get_number_of_cell_hidded() == self.model.get_number_of_bombs():
            self.is_win = True
            self.set_reset()

    def on_mouse_motion(self, x, y, dx, dy):
        """ Called when the player moves the mouse.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        dx, dy : float
            The movement of the mouse.

        """
        if self.exclusive:
            m = 0.15
            x, y = self.rotation
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y))
            self.rotation = (x, y)

    def on_key_press(self, symbol, modifiers):
        """ Called when the player presses a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """
        if symbol == key.Z:
            self.strafe[0] -= 1
        elif symbol == key.S:
            self.strafe[0] += 1
        elif symbol == key.Q:
            self.strafe[1] -= 1
        elif symbol == key.D:
            self.strafe[1] += 1
        elif symbol == key.A:
            self.model.display_bombs()
        elif symbol == key.E:
            if (self.is_losse or self.is_win):
                self.is_losse = False
                self.is_win = False
                self.set_reset()
            self.model.gen_demineur(True, self.is_win)
        elif symbol == key.SPACE:
            if self.jumped:
                print("set flying")
                self.flying = not self.flying
                self.jumping = False
            else:
                self.jumping = True
                self.jumped = True
        elif symbol == key.ESCAPE:
            self.set_exclusive_mouse(False)
        elif symbol == key.LSHIFT:
            self.crouch = True
            if self.sprinting:
                self.fov_offset -= SPRINT_FOV
                self.sprinting = False
        elif symbol == key.R:
            if not self.crouch:
                if not self.sprinting:
                    self.fov_offset += SPRINT_FOV
                self.sprinting = True
        elif symbol == key.TAB:
            self.flying = not self.flying
        elif symbol in self.num_keys:
            index = (symbol - self.num_keys[0]) % len(self.inventory)
            self.block = self.inventory[index]

    def on_key_release(self, symbol, modifiers):
        """ Called when the player releases a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """
        if symbol == key.Z:
            self.strafe[0] += 1
        elif symbol == key.S:
            self.strafe[0] -= 1
        elif symbol == key.Q:
            self.strafe[1] += 1
        elif symbol == key.D:
            self.strafe[1] -= 1
        elif symbol == key.SPACE:
            self.jumping = False
            self.dy = 0
            if self.flying:
                self.jumped = False
        elif symbol == key.LSHIFT:
            self.crouch = False
            if self.flying:
                self.dy = 0

    def on_resize(self, width, height):
        """ Called when the window is resized to a new `width` and `height`.
        """
        # label
        self.label.y = height - 10
        # reticle
        if self.reticle:
            self.reticle.delete()
        x, y = self.width // 2, self.height // 2
        n = 10
        self.reticle = pyglet.graphics.vertex_list(4,
            ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
        )

    def set_2d(self):
        """ Configure OpenGL to draw in 2d.
        """
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, max(1, width), 0, max(1, height), -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_3d(self):
        """ Configure OpenGL to draw in 3d.
        """
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(PLAYER_FOV + self.fov_offset, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = self.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.position
        if self.crouch and not self.flying:
            glTranslatef(-x, -y+0.2, -z)
        else:
            glTranslatef(-x, -y, -z)

    def display_menu(self):
        menu = pyglet.image.load(MENU_PATH)
        self.clear()
        menu.blit(0,0 )


    def on_draw(self):
        """ Called by pyglet to draw the canvas.
        """
        self.clear()
        self.set_3d()
        glColor3d(1, 1, 1)
        self.model.batch.draw()
        self.draw_focused_block()
        self.set_2d()
        self.draw_label()
        self.draw_reticle()
        #self.display_menu()

    def draw_focused_block(self):
        """ Draw black edges around the block that is currently under the
        crosshairs.
        """
        vector = self.get_sight_vector()
        block = self.model.hit_test(self.position, vector)[0]
        if block:
            x, y, z = block
            vertex_data = cube_vertices(x, y, z, 0.51)
            glColor3d(0, 0, 0)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            pyglet.graphics.draw(24, GL_QUADS, ('v3f/static', vertex_data))
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def draw_label(self):
        """ Draw the label in the top left of the screen.
        """
        x, y, z = self.position
        #self.label.text = '%02d (%.2f, %.2f, %.2f) %d / %d' % (
         #   pyglet.clock.get_fps(), x, y, z,
          #  len(self.model._shown), len(self.model.world))
        self.label.text = "Bomb : {}, Revealed cell : {}, Hidded cell : {}".format(self.model.get_number_of_bombs(), self.model.get_number_of_cell_revealed(), self.model.get_number_of_cell_hidded())
        if self.is_losse:
            self.game_status.text = " GAME OVER"
        elif self.is_win:
            self.game_status.text = "WIN"
        else:
            self.game_status.text = ""
        self.label.draw()
        self.game_status.draw()

    def draw_reticle(self):
        """ Draw the crosshairs in the center of the screen.
        """
        glColor3d(0, 0, 0)
        self.reticle.draw(GL_LINES)