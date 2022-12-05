# Graphics Libraries and Game Engine Research

## Vpython / Glowscript
- Complete 3D graphics using python only.
- Gets transcompiled into Javascript
- Fairly good performance, have issues with it not properly using discrete GPU and utilizing only the integrated GPU

## Pygame

- A video regarding pygame's performance: https://www.youtube.com/watch?v=hnKocNdF9-U
- Raster graphics based
- 2D
- Basically a wrapper API around SDL which is Simple DirectMedia Layer
    - SDL is implemented in C and is included in the library as C binaries.
- Example of making a simple 3D engine using pygame and numpy: https://www.youtube.com/watch?v=M_Hx0g5vFko
- This one uses Modern OpenGL, numpy, and pygame: https://www.youtube.com/watch?v=eJDIsFJN4OQ


## Python Arcade
- Uses OpenGL
- Offloads work on the GPU so get way higher FPS when sprite count goes to 14k
    - More info: https://api.arcade.academy/en/latest/pygame_comparison.html#:~:text=With%20PyGame%2C%20most%20of%20the,happens%20on%20the%20GPU%20side
- 

## Pygame v Python Arcade
- A detailed analysis: https://api.arcade.academy/en/latest/pygame_comparison.html#:~:text=With%20PyGame%2C%20most%20of%20the,happens%20on%20the%20GPU%20side.
- 


## Pyglet
- Written in pure python
- As "advanced performance" with support for batching and GPU rendering.
- Looks like you can load 3D models and has shaders too. From https://www.youtube.com/watch?v=Y0BOFJoKRKo, performance looks pretty goode. 
- Looks like its used fairly closely with OpenGL (ex: https://medium.com/@yvanscher/opengl-and-pyglet-basics-1bd9f1721cc6)


## Pyglet v Pygame
- As exposed by https://www.youtube.com/watch?v=r428O_CMcpI&t=144s, pygame lacked vsync whereas pyglet had it. However, after looking at documentation for pygame, it looks like this has been added.


## PyBullet
- Real-Time Physics Simulation
- Used a ton in Robotics
- Supports 3D
- Ex: Kubric, which is built on top of pybullet and used Blender for rendering.
  - https://github.com/google-research/kubric

## PyEngine3D
- Open source OpenGL 3D Engine
- https://github.com/ubuntunux/PyEngine3D
- Amazing features https://www.youtube.com/watch?v=x9GVA7tCAdw&t=34s
- Works with pyBullet

## Panda3D
- https://www.panda3d.org/
- "Speed of C++ with the use of Python"
- Fully utilizes GPU
- Looks pretty good https://www.youtube.com/watch?v=t2eC6JsImwc
- Pirates of the Caribbean online was written using this
- Developed by Disney
- Example games: https://www.youtube.com/watch?v=jID2u758Qgs

## Ursina Engine
- Written in python
- Is a wrapper around Panda3D
- Performance seems great, can make 2D Games, 3D games, applications, UIs etc. 
- 3D Snake Game by Coder Space: https://www.youtube.com/watch?v=YZnOvc0qx_k
- 3D Rubrics Cube by Coder Space: https://www.youtube.com/watch?v=OR2_zQN_Gbk

## Honorable Mentions
- LOVR (https://lovr.org/), designed for VR and uses Lua for scripting (same as Teardown (the game))

# Other Stuff

## Great YouTubers on the Subject
- ChiliTomatoNoodle @ChiliTomatoNoodle (C++, DirectX, 3D Graphics, Game Design)
- Coder Space, @CoderSpaceChannel (Python, 2D and 3D Graphics, Game Design)

## Random Super Cool Stuff
- https://www.youtube.com/shorts/h5PuIm6fRr8