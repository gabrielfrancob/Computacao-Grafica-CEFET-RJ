from PIL import Image
from OpenGL import GL
from array import array
import ctypes
import glfw
import glm
import math

VERTEX_SHADER = """
#version 400

layout (location=0) in vec3 attr_posicao;
layout (location=1) in vec3 attr_normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 normal;
out vec3 fragCoord;

void main(void) 
{
    gl_Position = projection * view * model * vec4(attr_posicao,1.0f);
    fragCoord = vec3(model * vec4(attr_posicao,1.0f));
    normal = mat3(transpose(inverse(model))) * attr_normal;
}
"""

FRAGMENT_SHADER = """
#version 400

in vec3 normal;
out vec4 fragColor;
in vec3 fragCoord;

uniform sampler2D textureSampler;

void main(void) 
{
    float ambientCoef = 0.2f;
    vec3 lightColor = vec3(1.0f, 1.0f, 1.0f);
    vec3 lightPos = vec3(0.0f,5.0f,5.0f);

    // vec3 objectColor = vec3(1.0f,0.0f,0.0f);

    vec3 norm = normalize(normal);
    vec3 lightDir = normalize(lightPos - fragCoord);
    float difCoef = max(dot(norm,lightDir),0.0f);
    vec3 ambientColor = ambientCoef*lightColor;
    vec3 diffuseColor = difCoef*lightColor;

    vec3 finalColor = (ambientColor + diffuseColor);
    fragColor = texture(textureSampler, vec2(gl_FragCoord.x / 800.0, gl_FragCoord.y / 600.0)) * vec4(finalColor, 1.0f);
}
"""
def compilaShaders():
    error = None
    progId = GL.glCreateProgram()
    for type, source in [ (GL.GL_VERTEX_SHADER, VERTEX_SHADER), (GL.GL_FRAGMENT_SHADER, FRAGMENT_SHADER) ]:
        shaderId = GL.glCreateShader(type)
        GL.glShaderSource(shaderId,[source])
        GL.glCompileShader(shaderId)
        status = GL.glGetShaderiv(shaderId,GL.GL_COMPILE_STATUS)
        if not status:
            error = GL.glGetShaderInfoLog(shaderId)
            GL.glDeleteShader(shaderId)
            break
        else:
            GL.glAttachShader(progId,shaderId)
    if error == None:
        GL.glLinkProgram(progId)
        status = GL.glGetProgramiv(progId,GL.GL_LINK_STATUS)
        if not status:
            error = GL.glGetProgramInfoLog(progId)
        else:
            return progId
    for shaderId in GL.glGetAttachedShaders(progId):
        GL.glDetachShader(progId, shaderId)
        GL.glDeleteShader(shaderId)
    GL.glDeleteProgram(progId)
    raise Exception(error)




def f(u,v):
    theta = (u*math.pi)-math.pi/2
    phi = v*2*math.pi
    r = 2
    x = r*math.cos(theta)*math.cos(phi)
    y = r*math.sin(theta)
    z = r*math.cos(theta)*math.sin(phi)
    return x, y, z


def indiceMalha(M=4,N=4):
    indices = array('H')
    for i in range(N-1):
        if i != 0:
            indices.append(i*M)
        for j in range(M):
            indices.append(i*M+j)
            indices.append((i+1)*M+j)
        indices.append((i+1)*M+M-1)
    return indices

def posicao(M=4,N=4):
    posicao = array('f')
    for i in range(N):
        v = i/(N-1)
        for j in range(M):
            u = j/(M-1)
            x, y, z = f(u,v)
            posicao.append(x)
            posicao.append(y)
            posicao.append(z)
    return posicao

def normal(M=4,N=4):
    normal = array('f')
    for i in range(N):
        v = i/(N-1)
        for j in range(M):
            u = j/(M-1)
            x, y, z = f(u,v)
            normal.append(x)
            normal.append(y)
            normal.append(z)
    return normal

tamIndice = 0

def malha(): 
    global tamIndice

    M = 50
    N = 50
    aPosicao = posicao(M,N)
    aNormal = normal(M,N)
    aIndices = indiceMalha(M,N)

    tamIndice = len(aIndices)
    VAO = GL.glGenVertexArrays(1)
    GL.glBindVertexArray(VAO)
    GL.glEnableVertexAttribArray(0) # Atributo da posicao
    GL.glEnableVertexAttribArray(1) # Atributo da normal

    VBO_posicao = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, VBO_posicao)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, len(aPosicao)*aPosicao.itemsize, ctypes.c_void_p(aPosicao.buffer_info()[0]), GL.GL_STATIC_DRAW)
    GL.glVertexAttribPointer(0,3,GL.GL_FLOAT,GL.GL_FALSE,0,ctypes.c_void_p(0))

    VBO_normal = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, VBO_normal)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, len(aNormal)*aNormal.itemsize, ctypes.c_void_p(aNormal.buffer_info()[0]), GL.GL_STATIC_DRAW)
    GL.glVertexAttribPointer(1,3,GL.GL_FLOAT,GL.GL_FALSE,0,ctypes.c_void_p(0))

    VBO_indice = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, VBO_indice)
    GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, len(aIndices)*aIndices.itemsize, ctypes.c_void_p(aIndices.buffer_info()[0]), GL.GL_STATIC_DRAW)

    return VAO

def carregar_textura():
    textura = Image.open("terra.png") 
    textura = textura.transpose(Image.FLIP_TOP_BOTTOM)
    largura, altura = textura.size

    dados_textura = list(textura.getdata())
    dados_textura = [componente / 255.0 for pixel in dados_textura for componente in pixel]

    textura_id = GL.glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, textura_id)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGB, largura, altura, 0, GL.GL_RGB, GL.GL_FLOAT, dados_textura)
    GL.glGenerateMipmap(GL.GL_TEXTURE_2D)

    return textura_id

def inicializa():
    global progId, malhaVAO, texturaID
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_MULTISAMPLE)
    progId = compilaShaders()
    malhaVAO = malha()
    texturaID = carregar_textura()

a = 0
def desenha():
    global a
    GL.glClearColor(0.0, 0.0, 0.0, 1.0)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT|GL.GL_DEPTH_BUFFER_BIT)

    projection = glm.perspective(math.pi/4,800/600,0.1,100)
    view = glm.lookAt(glm.vec3(0,2,12),glm.vec3(0,0,0),glm.vec3(0,1,0)) * glm.rotate(a,glm.vec3(1,0,0))

    model = glm.mat4(1.0)
    model = glm.rotate(model, a, glm.vec3(0, 1, 0))

    GL.glBindVertexArray(malhaVAO)
    GL.glUseProgram(progId)
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(progId, "model"),1,GL.GL_FALSE,glm.value_ptr(model))
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(progId, "view"),1,GL.GL_FALSE,glm.value_ptr(view))
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(progId, "projection"),1,GL.GL_FALSE,glm.value_ptr(projection))
    GL.glDrawElements(GL.GL_TRIANGLE_STRIP,tamIndice,GL.GL_UNSIGNED_SHORT,ctypes.c_void_p(0))

    GL.glActiveTexture(GL.GL_TEXTURE0)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texturaID)
    GL.glUniform1i(GL.glGetUniformLocation(progId, "textureSampler"), 0)

    GL.glDrawElements(GL.GL_TRIANGLE_STRIP, tamIndice, GL.GL_UNSIGNED_SHORT, ctypes.c_void_p(0))

    a += 0.0005


def main():
    if not glfw.init():
        return
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
    glfw.window_hint(glfw.SAMPLES, 4)
    window = glfw.create_window(800, 600, "Malha", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    inicializa()
    while not glfw.window_should_close(window):
        desenha()
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
