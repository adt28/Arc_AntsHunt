"""
Arc_AntsHunt - Python Arcade
A.D. Tejpal : 24-Apr-2021
=======================

This game, developed in python arcade, demonstrates intelligent
activities by a group of ants.

In idle state, there are 8 ants (4 big & 4 small) in the nest.
Whenever any fresh spider appears on the screen, a pair of big ants
(out of available idle ones) lock onto it. They rush outward, capture
the spider and drag it to Spider Prison, before returning to ant's nest.

Whenever any fresh leaf appears on the screen, a pair of small ants
(out of available idle ones) lock onto it. They rush outward, collect 
the leaf and drag it to Leaf Store, before returning to ants nest.

Left click of mouse spawns a fresh animated spider while right click
creates a new leaf floating downward in oscillating pattern.

Note: 
To be effective, the mouse click should not be too close to ants nest.
"""
import arcade
import random
import math
import os

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 560
SCREEN_TITLE = "Arcade Ants Hunt"
FPS = 30   # Frames per sec

SCALING_LEAF = 1.4
SCALING_BIG_ANT = 1.2
SCALING_SMALL_ANT = 0.8
SCALING_SPIDER = 1.0

COUNT_ANTS = 8
COUNT_SPIDERS = 4
COUNT_LEAFS = 4
SPEED_BIG_ANT = 3.0
SPEED_SMALL_ANT = 2.5

NEST_RADIUS = 120
STORE_RADIUS = (
    SCREEN_HEIGHT - 10 - 2 * NEST_RADIUS) / 4
PRISON_RADIUS = STORE_RADIUS
NEST_CENTER_X = SCREEN_WIDTH - NEST_RADIUS - 10
NEST_CENTER_Y = SCREEN_HEIGHT / 2
STORE_CENTER_X = NEST_CENTER_X
STORE_CENTER_Y = (
    NEST_CENTER_Y
    + NEST_RADIUS
    + STORE_RADIUS)
PRISON_CENTER_X = NEST_CENTER_X
PRISON_CENTER_Y = (
    NEST_CENTER_Y
    - NEST_RADIUS
    - PRISON_RADIUS)

class Ant(arcade.Sprite):

    def __init__(self, imgFile, scaleFactor, speed):

        super().__init__(imgFile, scaleFactor)

        self.targetSprite = None

        # For angular squiggle
        self.dTilt = 0.5  # degrees
        self.tiltMin = -2.5
        self.tiltMax = 2.5
        self.tilt = 0

        # For perpetual linear movement within defined boundaries
        # speed argument is supplied while creating the Ant() object
        # in class GamePlay.
        self.speed = speed

        self.xMin = NEST_CENTER_X - 0.7 * NEST_RADIUS
        self.yMin = NEST_CENTER_Y - 0.7 * NEST_RADIUS
        self.xMax = self.xMin + 1.4 * NEST_RADIUS
        self.yMax = self.yMin + 1.4 * NEST_RADIUS
        self.dx = 0.3
        self.dy = 0.3

        # Mode:
        # 0 - Idling in nest.
        # 1 - Moving outward to capture target.
        # 2 - Carrying target to holding point (Store or Prison).
        # 3 - Returning to nest after completion of job.
        self.mode = 0

        # Hit Rank:
        # (Used for re-positioning of ant pair after hitting the target)
        # 1 - It is the first ant to hit the given target
        # 2 - It is the 2nd ant to hit the given target
        self.hitRank = 0

    def chaseTarget(self):
        """
        This function handles ant activities covering tracking &
        capture of target, dragging it to holding point (Spider Prison
        or Leaf Store) and finally - return to ants nest.

        Note:
            change_x & change_y are built-in attributes of
            arcade.Sprite class
        """
        # No action if there is no target assigned
        if not self.targetSprite:
            return
                
        # Get the destination location
        if self.mode == 1:
            # It is outward trip towards the target.
            dest_x = self.targetSprite.center_x
            dest_y = self.targetSprite.center_y
        elif self.mode == 2:
            # Dragging the target to holding point.
            if self.targetSprite.guid == "S":
                # If Spider - To Prison
                dest_x = PRISON_CENTER_X
                dest_y = PRISON_CENTER_Y
            else:
                # If Leaf - To Store
                dest_x = STORE_CENTER_X
                dest_y = STORE_CENTER_Y
        else:
            # Return To Nest
            dest_x = NEST_CENTER_X
            dest_y = NEST_CENTER_Y

        # Distance upto destination
        span = self.getDiagonal(
            dest_x - self.center_x, 
            dest_y - self.center_y)

        # Accelerate on approaching target by using
        # multiplying  factor mf
        if self.mode == 1:
            if span < 100:
                mf = 12
            elif span < 200:
                mf = 6
            elif span < 300:
                mf = 3
            else:
                mf = 1
        else:
            # Return at a uniform speed, faster than normal
            mf = 4

        # If too close to the target, snap into it & start return journey
        # after both ants of the pair have hit the target.
        if span <= self.getDiagonal(
                    self.change_x * mf,  
                    self.change_y * mf):
            self.center_x = dest_x
            self.center_y = dest_y

            if self.mode == 1:
                # We have reached the end of outward trip
                # Prepare for moving to holding point:
                self.targetSprite.hitCount = self.targetSprite.hitCount + 1

                # Assign hitRank
                # (i.e. whether the ant is first or second one to hit the target)
                if self.hitRank == 0:
                    self.hitRank = self.targetSprite.hitCount

                # Reposition the ant pair as per hitRank
                if self.hitRank > 1:
                    self.center_x = self.targetSprite.center_x + 5
                    self.center_y = self.targetSprite.center_y + 5
                else:
                    self.center_x = self.targetSprite.center_x - 5
                    self.center_y = self.targetSprite.center_y - 5

                # Set the velocity based upon normallized vector
                # taking into account the pertinent holding point.
                if self.targetSprite.guid == "S":
                    self.setVelocity(
                        PRISON_CENTER_X, 
                        PRISON_CENTER_Y)
                else:
                    self.setVelocity(
                        STORE_CENTER_X, 
                        STORE_CENTER_Y)
                
                # Set the mode for moving to holding point
                self.mode = 2

            elif self.mode == 2:
                # We have reached the holding point
                if self.targetSprite.guid == "S":
                    self.targetSprite.center_x = PRISON_CENTER_X
                    self.targetSprite.center_y = PRISON_CENTER_Y
                    self.scatter(self.targetSprite, 0.7 * PRISON_RADIUS)
                else:
                    self.targetSprite.center_x = STORE_CENTER_X
                    self.targetSprite.center_y = STORE_CENTER_Y
                    self.scatter(self.targetSprite, 0.7 * STORE_RADIUS)
                    
                # Proceed to the nest now
                self.setVelocity(
                    NEST_CENTER_X, 
                    NEST_CENTER_Y)

                # Set the mode for returning to ants nest
                self.mode = 3

            elif self.mode == 3:
                # We have returned to ants nest

                # Stop motion
                self.change_x = 0
                self.change_y = 0
                self.hitRank = 0

                # Reposition the returning ants via random scatter
                self.scatter(self, 0.7 * NEST_RADIUS)
                
                # Set the mode to idle
                self.mode = 0

                # Job Finished - De-assign targetSprite
                self.targetSprite = None

        else:
            # Make sure outward or inward movement takes
            # place only when a pair of ants is active for same target
            if ((self.mode <= 1 
                        and  self.targetSprite.lockCount > 1)
                        or (self.mode > 1 
                        and  self.targetSprite.hitCount > 1)):
                self.center_x += self.change_x * mf
                self.center_y += self.change_y * mf

                if self.mode == 2:
                    # Drag the target to holding point
                    # by linking it to ant movement.
                    self.targetSprite.center_x = self.center_x + 5
                    self.targetSprite.center_y = self.center_y + 5

        # Constant tracking of moving target.
        if self.mode == 1:
            self.setVelocity(dest_x, dest_y)         

    def setVelocity(self, dest_x, dest_y):
        # Calculate the angle in radians between the start points
        # and end points. This is the angle the ant will follow.
        x_diff = dest_x - self.center_x
        y_diff = dest_y - self.center_y

        # Vector angle in radians
        angle = math.atan2(y_diff, x_diff)

        # Taking into account the angle, calculate change_x
        # and change_y. Velocity is how fast the ant travels.
        self.change_x = math.cos(angle) * self.speed
        self.change_y = math.sin(angle) * self.speed

        # Rotate the ant so as to point towards destination.
        # Sprite angle is to be applied in degrees
        self.angle = math.degrees(angle)

    def getDiagonal(self, spanX, spanY):
        return math.sqrt(spanX**2 + spanY**2)

    def getVectorAngleRadians(
                    self, startX, startY, destX, destY):
        return math.atan2(
            (destY - startY), (destX - startX))

    def getVectorAngleDegrees(
                    self, startX, startY, destX, destY):
        return math.degrees(
            self.getVectorAngleRadians(
            startX, startY, destX, destY))

    def scatter(self, mySprite, halfRange):
        # Random scattering of sprite object within given range.
        hr = int(halfRange)
        fr = 2 * hr
        mySprite.center_x = \
            mySprite.center_x + random.randrange(fr) - hr
        mySprite.center_y = \
            mySprite.center_y + random.randrange(fr) - hr

    def animate(self):
        # Some squiggling animation:
        self.tilt = self.tilt + self.dTilt
        
        if self.tilt > self.tiltMax:
            self.dTilt = -self.dTilt
            self.tilt = self.tiltMax

        if self.tilt < self.tiltMin:
            self.dTilt = -self.dTilt
            self.tilt = self.tiltMin

        self.angle = self.angle + self.tilt

    def idleMove(self):
        # Perpetual movement within specified boundaries
        if self.mode != 0:
            return

        self.center_x = self.center_x + self.dx
        if self.center_x > self.xMax:
            self.dx = - self.dx
            self.center_x = self.xMax

        if self.center_x < self.xMin:
            self.dx = - self.dx
            self.center_x = self.xMin

        self.center_y = self.center_y + self.dy
        if self.center_y > self.yMax:
            self.dy = - self.dy
            self.center_y = self.yMax

        if self.center_y < self.yMin:
            self.dy = - self.dy
            self.center_y = self.yMin

class Leaf(arcade.Sprite):
    def __init__(self, imgFile, scaleFactor, centerX):
        super().__init__(imgFile, scaleFactor)
        self.lockCount = 0
        self.hitCount = 0

        # For angular oscillation
        self.dTilt = 0.2  # degrees
        self.tiltMin = -2.5
        self.tiltMax = 2.5
        self.tilt = 0

        # For horizontal oscillation while floating downwards.
        self.dx = 1.0
        self.dy = -0.9
        self.xMin = centerX - 30
        self.xMax = centerX + 30
        self.yMin = 0
        self.yMax = SCREEN_HEIGHT

        # For time delay in sensing target
        self.timeDelay = 0

    def animate(self):
        # Some squiggling animation:
        if self.hitCount > 0:
            return

        # Angular oscillation
        self.tilt = self.tilt + self.dTilt
        
        if self.tilt > self.tiltMax:
            self.dTilt = -self.dTilt
            self.tilt = self.tiltMax

        if self.tilt < self.tiltMin:
            self.dTilt = -self.dTilt
            self.tilt = self.tiltMin

        self.angle = self.angle + self.tilt

        # Horizontal oscillation while floating downwards.
        self.center_x = self.center_x + self.dx
        if self.center_x > self.xMax:
            self.dx = -self.dx
            self.center_x = self.xMax

        if self.center_x < self.xMin:
            self.dx = -self.dx
            self.center_x = self.xMin

        self.center_y = self.center_y + self.dy
        if self.center_y < self.yMin:
            self.center_y = self.yMax

class Spider(arcade.Sprite):
    def __init__(self, imgFile, scaleFactor):
        super().__init__(imgFile, scaleFactor)
        self.lockCount = 0
        self.hitCount = 0

        # For angular ooscillation
        self.dTilt = 0.5  # degrees
        self.tiltMin = -2.5
        self.tiltMax = 2.5
        self.tilt = 0

        # For perpetual movement within given boundaries.
        self.dx = 2.0
        self.dy = 3.5
        self.xMin = 0
        self.xMax = NEST_CENTER_X - NEST_RADIUS - 100
        self.yMin = 0
        self.yMax = SCREEN_HEIGHT

        # For time delay in sensing target
        self.timeDelay = 0
        
    def animate(self):
        # Some squiggling animation:
        if self.hitCount > 0:
            return

        # For angular ooscillation
        self.tilt = self.tilt + self.dTilt
        
        if self.tilt > self.tiltMax:
            self.dTilt = -self.dTilt
            self.tilt = self.tiltMax

        if self.tilt < self.tiltMin:
            self.dTilt = -self.dTilt
            self.tilt = self.tiltMin

        self.angle = self.angle + self.tilt

        # For perpetual movement within given boundaries.
        self.center_x = self.center_x + self.dx
        if self.center_x > self.xMax:
            self.dx = -self.dx
            self.center_x = self.xMax

        if self.center_x < self.xMin:
            self.dx = -self.dx
            self.center_x = self.xMin

        self.center_y = self.center_y + self.dy
        if self.center_y > self.yMax:
            self.dy = -self.dy
            self.center_y = self.yMax

        if self.center_y < self.yMin:
            self.dy = -self.dy
            self.center_y = self.yMin

class GamePlay(arcade.Window):
    """ Our custom Window Class"""

    def __init__(self):
        """ Initializer """       
        # Call the parent class initializer
        super().__init__(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            SCREEN_TITLE,
            update_rate=1/FPS)

        # Variables that will hold sprite lists
        self.antsBig = None
        self.antsBigIdle = None
        self.antsSmall = None
        self.antsSmallIdle = None
        self.leafs = None
        self.leafsFresh = None
        self.spiders = None
        self.spidersFresh = None

    def getTargetSpider(self, deltaTime):        
        if (len(self.spidersFresh) > 0
                    and len(self.antsBigIdle) > 1):

            spider = self.spidersFresh[0]
            # Time delay of 1.5 sec in sensing target
            spider.timeDelay = spider.timeDelay + deltaTime
            if spider.timeDelay > 1.5:
                spider.timeDelay = 0
                for n in range(2):
                    ant = self.antsBigIdle[n]
                    ant.mode = 1
                    ant.targetSprite = spider
                    ant.center_x = NEST_CENTER_X
                    if n > 0:
                        ant.center_y = NEST_CENTER_Y + 20
                    else:
                        ant.center_y = NEST_CENTER_Y - 20

                # Set the target sprite lock count
                spider.lockCount = spider.lockCount + 2

        for ant in self.antsBig:
            if ant.mode > 0:
                # The ant is no longer in idle mode
                # If both ants in the pair have locked on
                # the target, call chaseTarget() method in Ant class
                if ant.targetSprite.lockCount > 1:
                    ant.chaseTarget()

                # Remove active ant from idle list
                if ant in self.antsBigIdle:
                    self.antsBigIdle.remove(ant)
            else:
                # The ant is in idle mode. Append it to idle list.
                if not ant in self.antsBigIdle:
                    self.antsBigIdle.append(ant)

        for spider in self.spiders:
            # If the spider is targetted by more than one ant,
            # remove it from fresh list
            if spider.lockCount > 1 and spider in self.spidersFresh:
                self.spidersFresh.remove(spider)

    def getTargetLeaf(self, deltaTime):        
        if (len(self.leafsFresh) > 0
                    and len(self.antsSmallIdle) > 1):

            leaf = self.leafsFresh[0]
            # Time delay of 1.5 sec in sensing target
            leaf.timeDelay = leaf.timeDelay + deltaTime
            if leaf.timeDelay > 1.5:
                leaf.timeDelay = 0
                for n in range(2):
                    ant = self.antsSmallIdle[n]
                    ant.mode = 1
                    ant.targetSprite = leaf
                    ant.center_x = NEST_CENTER_X
                    if n > 0:
                        ant.center_y = NEST_CENTER_Y + 20
                    else:
                        ant.center_y = NEST_CENTER_Y - 20

                # Set the target sprite lock count
                leaf.lockCount = leaf.lockCount + 2

        for ant in self.antsSmall:
            if ant.mode > 0:
                # The ant is no longer in idle mode
                # If both ants in the pair have locked on
                # the target, call chaseTarget() method in Ant class
                if ant.targetSprite.lockCount > 1:
                    ant.chaseTarget()

                # Remove active ant from idle list
                if ant in self.antsSmallIdle:
                    self.antsSmallIdle.remove(ant)
            else:
                # The ant is in idle mode. Append it to idle list.
                if not ant in self.antsSmallIdle:
                    self.antsSmallIdle.append(ant)

        for leaf in self.leafs:
            # If the leaf is targetted by more than one ant,
            # remove it from fresh list
            if leaf.lockCount > 1 and leaf in self.leafsFresh:
                self.leafsFresh.remove(leaf)

    def setup(self):
        arcade.set_background_color((235, 235, 235))

        # Sprite lists
        self.antsBig = arcade.SpriteList()
        self.antsBigIdle = arcade.SpriteList()
        self.antsSmall = arcade.SpriteList()
        self.antsSmallIdle = arcade.SpriteList()
        self.leafs = arcade.SpriteList()
        self.leafsFresh = arcade.SpriteList()
        self.spiders = arcade.SpriteList()
        self.spidersFresh = arcade.SpriteList()

        # Create the leafs
        # Keep margin of 100 from ant's nest
        xRange = SCREEN_WIDTH - 2 * NEST_RADIUS - 100

        # First leaf at x value of 50
        spacing = (xRange - 50) / COUNT_LEAFS
        
        for n in range(COUNT_LEAFS):
            centerX = 50 + n * spacing
            leaf = Leaf(
                "leaf.png", SCALING_LEAF, centerX)
            leaf.guid = "L"
            leaf.center_x = centerX
            leaf.center_y = SCREEN_HEIGHT
            self.leafs.append(leaf)
            self.leafsFresh.append(leaf)

        # Create the spiders
        spacing = (SCREEN_HEIGHT - 40) / COUNT_SPIDERS
        for n in range(COUNT_SPIDERS):
            spider = Spider(
                "spider.png", SCALING_SPIDER)
            spider.guid = "S"
            spider.center_x = 20
            spider.center_y = 20 + n * spacing
            self.spiders.append(spider)
            self.spidersFresh.append(spider)

        # Create the ants, half big & half small
        rr = 0.7 * NEST_RADIUS
        halfCount = COUNT_ANTS // 2
        
        for n in range(COUNT_ANTS):
            if n < halfCount:
                ant = Ant(
                    "ant.png",
                    SCALING_BIG_ANT,
                    SPEED_BIG_ANT)
                ant.center_x = NEST_CENTER_X
                ant.center_y = NEST_CENTER_Y
                ant.scatter(ant, rr)
                self.antsBig.append(ant)
                self.antsBigIdle.append(ant)
            else:
                ant = Ant(
                    "ant.png",
                    SCALING_SMALL_ANT,
                    SPEED_SMALL_ANT)
                ant.center_x = NEST_CENTER_X
                ant.center_y = NEST_CENTER_Y
                ant.scatter(ant, rr)
                self.antsSmall.append(ant)
                self.antsSmallIdle.append(ant)

    def on_update(self, deltaTime):
        """ Movement and game logic """
        for ant in self.antsBig:
            ant.animate()
            ant.idleMove()

        for leaf in self.leafs:
            leaf.animate()
            
        for spider in self.spiders:
            spider.animate()

        for ant in self.antsSmall:
            ant.animate()
            ant.idleMove()

        self.getTargetSpider(deltaTime)
        self.getTargetLeaf(deltaTime)

    def on_draw(self):
        """ Draw everything """
        arcade.start_render()

        txt = "Left Click For New Spider.\n"
        txt = txt + "Right Click For New Leaf"
        tx = 40
        ty = 75
        arcade.draw_text(txt, tx, ty, arcade.color.BLACK, 26)

        txt = "Ants Hunt In Pairs\n"
        txt = txt + "For Spiders: Big Ants, "
        txt = txt + "For Leaves: Small Ants\n"
        txt = txt + "Deliberate Time Delay Of 1.5 sec In Sensing Target"
        ty = ty - 60
        arcade.draw_text(txt, tx, ty, arcade.color.BLACK, 18)
        

        txt = "LEAF STORE"
        tx = STORE_CENTER_X - STORE_RADIUS - 10
        ty = STORE_CENTER_Y - 20
        arcade.draw_text(
            txt, tx, ty, arcade.color.BLACK, 16, anchor_x="right")

        txt = "ANTS NEST"
        tx = NEST_CENTER_X - NEST_RADIUS - 10
        ty = NEST_CENTER_Y - 20
        arcade.draw_text(
            txt, tx, ty, arcade.color.BLACK, 16, anchor_x="right")

        txt = "SPIDER PRISON"
        tx = PRISON_CENTER_X - PRISON_RADIUS - 10
        ty = PRISON_CENTER_Y - 20
        arcade.draw_text(
            txt, tx, ty, arcade.color.BLACK, 16, anchor_x="right")

        # Draw circles for ant's nest, store & prison
        arcade.draw_circle_outline(
            NEST_CENTER_X,
            NEST_CENTER_Y, 
            NEST_RADIUS, (0, 0, 180), 4)
        arcade.draw_circle_outline(
            STORE_CENTER_X, 
            STORE_CENTER_Y, 
            STORE_RADIUS, (0, 180, 0), 4)
        arcade.draw_circle_outline(
            PRISON_CENTER_X, 
            PRISON_CENTER_Y, 
            PRISON_RADIUS, (180, 0, 0), 4)

        self.antsBig.draw()
        self.antsSmall.draw()
        self.spiders.draw()
        self.leafs.draw()

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        :param float x: x position of the mouse
        :param float y: y position of the mouse
        :param int button: What button was hit. One of:
            arcade.MOUSE_BUTTON_LEFT,
            arcade.MOUSE_BUTTON_RIGHT,
            arcade.MOUSE_BUTTON_MIDDLE
        :param int modifiers:
            Bitwise 'and' of all modifiers (shift, ctrl, num lock)
            pressed during this event. See :ref:`keyboard_modifiers`.
        """
        # No action if mouse click is too close to ants nest.
        if  x > NEST_CENTER_X - NEST_RADIUS - 100:
            return
        
        if button == arcade.MOUSE_BUTTON_LEFT:
            # Create Spider at clicked position
            spider = Spider(
                "spider.png", SCALING_SPIDER)
            spider.guid = "S"
            spider.center_x = x
            spider.center_y = y
            self.spiders.append(spider)
            self.spidersFresh.append(spider)
        else:
            # Create Leaf at clicked position
            leaf = Leaf(
                "leaf.png", SCALING_LEAF, x)
            leaf.guid = "L"
            leaf.center_x = x
            leaf.center_y = y
            self.leafs.append(leaf)
            self.leafsFresh.append(leaf)

#====================
def main():
    """ Main method """
    gp = GamePlay()
    gp.setup()
    arcade.run()

#====================
if __name__ == "__main__":
    main()
