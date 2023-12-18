#!/usr/bin/env python
# coding: utf-8

# In[20]:


import math
from OpenGL import GL
from array import array
import ctypes
import glfw
from PIL import Image
import glm
import numpy as np

VERTEX_SHADER = """
#version 400

layout (location=0) in vec3 position;
layout (location=1) in vec2 textura;
out vec2 fsTextura;

uniform mat4 mvp;

void main(void) 
{
    fsTextura = textura;
    gl_Position = mvp * vec4(position, 1.0f);
}
"""

FRAGMENT_SHADER = """
#version 400

uniform sampler2D textureSlot;
in vec2 fsTextura;
out vec4 color;

void main(void) 
{
    color = texture(textureSlot, fsTextura);
}
"""

def compilaShaders():
    error = None
    progId = GL.glCreateProgram()
    for type, source in [
        (GL.GL_VERTEX_SHADER, VERTEX_SHADER),
        (GL.GL_FRAGMENT_SHADER, FRAGMENT_SHADER),
    ]:
        shaderId = GL.glCreateShader(type)
        GL.glShaderSource(shaderId, [source])
        GL.glCompileShader(shaderId)
        status = GL.glGetShaderiv(shaderId, GL.GL_COMPILE_STATUS)
        if not status:
            error = GL.glGetShaderInfoLog(shaderId)
            GL.glDeleteShader(shaderId)
            break
        else:
            GL.glAttachShader(progId, shaderId)
    if error is None:
        GL.glLinkProgram(progId)
        status = GL.glGetProgramiv(progId, GL.GL_LINK_STATUS)
        if not status:
            error = GL.glGetProgramInfoLog(progId)
        else:
            return progId
    for shaderId in GL.glGetAttachedShaders(progId):
        GL.glDetachShader(progId, shaderId)
        GL.glDeleteShader(shaderId)
    GL.glDeleteProgram(progId)
    raise Exception(error)

def cubo():
    posicao = array(
        "f", [
            -0.5, 0.5, -0.5,    # V0 0
            -0.5, 0.5, -0.5,    # V0 1 
            -0.5, 0.5, -0.5,    # V0 2
            0.5, 0.5, -0.5,     # V1 3
            0.5, 0.5, -0.5,     # V1 4
            -0.5, 0.5, 0.5,     # V2 5
            0.5, 0.5, 0.5,      # V3 6
            -0.5, -0.5, -0.5,   # V4 7
            -0.5, -0.5, -0.5,   # V4 8
            -0.5, -0.5, -0.5,   # V4 9
            -0.5, -0.5, 0.5,    # V5 10
            0.5, -0.5, 0.5,     # V6 11
            0.5, -0.5, -0.5,    # V7 12
            0.5, -0.5, -0.5     # V7 13
        ]
    )
   
    texture = array("f", [
        1/4, 1,    # 0 1 0
        0, 2/3,    # 0 2 1  
        1, 2/3,    # 0 3 2
        2/4, 1,    # 1 1 3
        3/4, 2/3,  # 1 2 4
        1/4, 2/3,  # 2   5
        2/4, 2/3,  # 3   6
        0,  1/3,   # 4 1 7
        1,  1/3,   # 4 2 8
        1/4,  0,   # 4 3 9
        1/4, 1/3,  # 5   10
        2/4, 1/3,  # 6   11
        3/4, 1/3,  # 7 1 12
        2/4, 0     # 7 2 13
        
    ])

    indices = array("I", [
        5, 10, 11, 11, 5, 6,  # Face frontal ok
        6, 11, 12, 12, 6, 4,  # Face direita ok
        4, 12, 8, 8, 4, 2,  # Face traseira ok
        5, 10, 1, 1, 10, 7,  # Face esquerda 
        5, 0, 6, 6, 0, 3,  # Face superior ok
        10, 9, 13, 13, 10, 11   # Face inferior ok
    ])

    VAO = GL.glGenVertexArrays(1)
    GL.glBindVertexArray(VAO)

    VBO = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, VBO)
    GL.glBufferData(
        GL.GL_ARRAY_BUFFER,
        len(posicao) * posicao.itemsize,
        ctypes.c_void_p(posicao.buffer_info()[0]),
        GL.GL_STATIC_DRAW,
    )
    GL.glEnableVertexAttribArray(0)
    GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, ctypes.c_void_p(0))

    VBO = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, VBO)
    GL.glBufferData(
        GL.GL_ARRAY_BUFFER,
        len(texture) * texture.itemsize,
        ctypes.c_void_p(texture.buffer_info()[0]),
        GL.GL_STATIC_DRAW,
    )
    GL.glEnableVertexAttribArray(1)
    GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 0, ctypes.c_void_p(0))

    EBO = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, EBO)
    GL.glBufferData(
        GL.GL_ELEMENT_ARRAY_BUFFER,
        len(indices) * indices.itemsize,
        ctypes.c_void_p(indices.buffer_info()[0]),
        GL.GL_STATIC_DRAW,
    )

    return VAO, len(indices)

def loadTexture(filename):
    im = Image.open(filename)
    w, h = im.size
    if im.mode == "RGBA":
        modo = GL.GL_RGBA
        data = im.tobytes("raw", "RGBA", 0, -1)
    else:
        modo = GL.GL_RGB
        data = im.tobytes("raw", "RGB", 0, -1)
    textureId = GL.glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, textureId)
    GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, modo, w, h, 0, modo, GL.GL_UNSIGNED_BYTE, data)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
    return textureId

def inicializa():
    global progId, cuboVAO, num_indices
    progId = compilaShaders()
    cuboVAO, num_indices = cubo()
    GL.glUseProgram(progId)
    GL.glActiveTexture(GL.GL_TEXTURE0)
    loadTexture("dado.png")
    GL.glUniform1i(GL.glGetUniformLocation(progId, "textureSlot"), 0)

rotation_angle = 0
def desenha():
    global rotation_angle
    GL.glClearColor(0.2, 0.3, 0.3, 1.0)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    rotation_angle += 0.01  # Incremento do ângulo de rotação

    projection = glm.perspective(math.pi/4,800/600,0.1,100)
    camera = glm.lookAt(glm.vec3(0,1.5,3),glm.vec3(0,0,0),glm.vec3(0,1,0))


    model = glm.translate(glm.vec3(0,0,0)) * glm.rotate(rotation_angle,glm.vec3(0,1,0))
    mvp = projection * camera * model

    GL.glUseProgram(progId)
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(progId, "mvp"),1,GL.GL_FALSE,glm.value_ptr(mvp))

    GL.glBindVertexArray(cuboVAO)
    GL.glDrawElements(GL.GL_TRIANGLES, num_indices, GL.GL_UNSIGNED_INT, None)

def main():
    if not glfw.init():
        return
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
    window = glfw.create_window(800, 600, "Cubo Texturizado", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.swap_interval(1)  # Ativa a sincronização vertical (V-Sync)
    GL.glEnable(GL.GL_DEPTH_TEST)  # Ativa o teste de profundidade
    inicializa()
    while not glfw.window_should_close(window):
        desenha()
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()

