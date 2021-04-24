"""
Arc_AntsHunt - Python Arcade
A.D. Tejpal : 24-Apr-2021
======================

This game, developed in python arcade, demonstrates intelligent
activities by a group of ants.

In idle state, there are 8 ants (4 big & 4 small), moving about in the nest.
Whenever any fresh spider appears on the screen, a pair of big ants
(out of available idle ones) lock onto it. They rush outward, capture
the spider and drag it to Spider Prison, before returning to ants nest.

Whenever any fresh leaf appears on the screen, a pair of small ants
(out of available idle ones) lock onto it. They rush outward, collect 
the leaf and drag it to Leaf Store, before returning to ant's nest.

Left click of mouse spawns a fresh animated spider while right click
creates a new leaf floating downward in oscillating pattern.

Note: 
To be effective, the mouse click should not be too close to ants nest.