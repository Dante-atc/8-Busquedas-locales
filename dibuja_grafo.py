#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
dibuja_grafo.py
------------

Dibujar un grafo utilizando métodos de optimización

Estos métodos no son los que se utilizan en el dibujo de
gráfos por computadora pero da una idea de la utilidad de los métodos de
optimización en un problema divertido.

Para realizar este problema es necesario contar con el módulo Pillow
instalado (en Anaconda se instala por default. Si no se encuentra instalado,
desde la termnal se puede instalar utilizando

$pip install pillow

"""

__author__ = 'Dante Alejandro Tostado Cortes'

import blocales
import random
import itertools
import math
import time
from PIL import Image, ImageDraw


class problema_grafica_grafo(blocales.Problema):

    """
    Clase para el dibujo de un grafo simple no dirigido

    """

    def __init__(self, vertices, aristas, dimension_imagen=400):
        """
        Un grafo se define como un conjunto de vertices, en forma de
        lista (no conjunto, el orden es importante a la hora de
        graficar), y un conjunto (tambien en forma de lista) de pares
        ordenados de vertices, lo que forman las aristas.

        Igualmente es importante indicar la resolución de la imagen a
        mostrar (por default de 400x400 pixeles).

        @param vertices: Lista con el nombre de los vertices.
        @param aristas: Lista con pares de vertices, los cuales
                        definen las aristas.
        @param dimension_imagen: Entero con la dimension de la imagen
                                 en pixeles (cuadrada por facilidad).

        """
        self.vertices = vertices
        self.aristas = aristas
        self.dim = dimension_imagen

        # Adyacencia precalculada: lista de vecinos por vertice.
        self.adyacencia = {v: [] for v in vertices}
        for (a, b) in aristas:
            self.adyacencia[a].append(b)
            self.adyacencia[b].append(a)

    def estado_aleatorio(self):
        """
        Devuelve un estado aleatorio.

        Un estado para este problema de define como:

           s = [s(1), s(2),..., s(2*len(vertices))],

        en donde s(i) \\in {10, 11, ..., self.dim - 10} es la posición
        en x del nodo i/2 si i es par, o la posicion en y
        del nodo (i-1)/2 si i es non y(osease las parejas (x,y)).

        @return: Una tupla con las posiciones (x1, y1, x2, y2, ...) de
                 cada vertice en la imagen.

        """
        return tuple(random.randint(10, self.dim - 10) for _ in
                     range(2 * len(self.vertices)))

    def vecinos(self, estado):
        """
        Generador de los vecinos de un estado. En este caso, el
        vecino se obtiene cambiando la posición de un vértice en
        forma aleatoria.

        @param estado: Una tupla con el estado.

        @return: Un generador de estados vecinos

        """
        for i in range(len(estado)):
            vecino = list(estado)
            vecino[i] = max(10,
                            min(self.dim - 10,
                                vecino[i] + random.randint(-10, 10)))
            yield tuple(vecino)

    def vecino_aleatorio(self, estado, dmax=40):
        """
        Encuentra un vecino en forma aleatoria.

        En lugar de mover una sola coordenada (lo que produce pasos muy
        pequeños y direcciones siempre horizontales o verticales), se mueve
        un vértice completo (sus dos coordenadas x,y) en una dirección
        aleatoria continua y con magnitud gaussiana. Así el vecino explora
        el plano en cualquier dirección y la dispersión se puede acoplar a
        la calendarización del temple.

        @param estado: Una tupla con el estado.
        @param dmax: Desviación máxima (en pixeles) del desplazamiento.

        @return: Una tupla con un estado vecino al estado de entrada.

        """
        vecino = list(estado)
        # selecciona un vertice completo (par de coordenadas x,y)
        v = random.randint(0, len(self.vertices) - 1)
        dx = random.gauss(0, dmax)
        dy = random.gauss(0, dmax)
        vecino[2 * v] = int(max(10, min(self.dim - 10, vecino[2 * v] + dx)))
        vecino[2 * v + 1] = int(max(10, min(self.dim - 10, vecino[2 * v + 1] + dy)))
        return tuple(vecino)

    def costo(self, estado):
        """
        Encuentra el costo de un estado. En principio el costo de un estado
        es la cantidad de veces que dos aristas se cruzan cuando se dibujan.

        Esto hace que el dibujo se organice para tener el menor numero
        posible de cruces entre aristas.

        @param: Una tupla con un estado

        @return: Un número flotante con el costo del estado.

        """
        # Los cruces son el criterio dominante: un cruce arruina la claridad
        # más que cualquier otro defecto, así que K1 es el más alto. La
        # separación y el ángulo son cosméticos pero importantes, con pesos
        # intermedios. El criterio propio (centrado) solo desempata.
        K1 = 10.0
        K2 = 2.0
        K3 = 3.0
        K4 = 1.0

        # Genera un diccionario con el estado y la posición
        estado_dic = self.estado2dic(estado)

        return (K1 * self.numero_de_cruces(estado_dic) +
                K2 * self.separacion_vertices(estado_dic) +
                K3 * self.angulo_aristas(estado_dic) +
                K4 * self.criterio_propio(estado_dic))

    def numero_de_cruces(self, estado_dic):
        """
        Devuelve el numero de veces que dos aristas se cruzan en el grafo
        si se grafica como dice estado_dic

        @param estado_dic: Diccionario cuyas llaves son los vértices
                           del grafo y cuyos valores es una tupla con
                           la posición (x, y) de ese vértice en el
                           dibujo.

        @return: Un número.

        """
        total = 0

        # Por cada arista en relacion a las otras (todas las combinaciones de
        # aristas)
        for (aristaA, aristaB) in itertools.combinations(self.aristas, 2):

            # Encuentra los valores de (x0A,y0A), (xFA, yFA) para los
            # vertices de una arista y los valores (x0B,y0B), (x0B,
            # y0B) para los vertices de la otra arista
            (x0A, y0A) = estado_dic[aristaA[0]]
            (xFA, yFA) = estado_dic[aristaA[1]]
            (x0B, y0B) = estado_dic[aristaB[0]]
            (xFB, yFB) = estado_dic[aristaB[1]]

            # Utilizando la clasica formula para encontrar
            # interseccion entre dos lineas cuidando primero de
            # asegurarse que las lineas no son paralelas (para evitar
            # la división por cero)
            den = (xFA - x0A) * (yFB - y0B) - (xFB - x0B) * (yFA - y0A)
            if den == 0:
                continue

            # Y entonces sacamos el largo del cruce, normalizado por
            # den. Esto significa que en 0 se encuentran en la primer
            # arista y en 1 en la última. Si los puntos de cruce de
            # ambas lineas se encuentran en valores entre 0 y 1,
            # significa que se cruzan
            puntoA = ((xFB - x0B) * (y0A - y0B) -
                      (yFB - y0B) * (x0A - x0B)) / den
            puntoB = ((xFA - x0A) * (y0A - y0B) -
                      (yFA - y0A) * (x0A - x0B)) / den
            if 0 < puntoA < 1 and 0 < puntoB < 1:
                total += 1
        return total

    def separacion_vertices(self, estado_dic, min_dist=50):
        """
        A partir de una posicion "estado" devuelve una penalización
        proporcional a cada par de vertices que se encuentren menos
        lejos que min_dist. Si la distancia entre vertices es menor a
        min_dist, entonces calcula una penalización proporcional a
        esta.

        @param estado_dic: Diccionario cuyas llaves son los vértices
                           del grafo y cuyos valores es una tupla con
                           la posición (x, y) de ese vértice en el
                           dibujo.  @param min_dist: Mínima distancia
                           aceptable en pixeles entre dos vértices en
                           el dibujo.

        @return: Un número.

        """
        total = 0
        for (v1, v2) in itertools.combinations(self.vertices, 2):
            # Calcula la distancia entre dos vertices
            (x1, y1), (x2, y2) = estado_dic[v1], estado_dic[v2]
            dist = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

            # Penaliza la distancia si es menor a min_dist
            if dist < min_dist:
                total += (1.0 - (dist / min_dist))
        return total

    def angulo_aristas(self, estado_dic):
        """
        A partir de una posicion "estado", devuelve una penalizacion
        proporcional a cada angulo entre aristas menor a pi/6 rad (30
        grados). Los angulos de pi/6 o mayores no llevan ninguna
        penalización, y la penalizacion crece conforme el angulo es
        menor.

        @param estado_dic: Diccionario cuyas llaves son los vértices
                           del grafo y cuyos valores es una tupla con
                           la posición (x, y) de ese vértice en el
                           dibujo.

        @return: Un número.

        """
        total = 0.0
        umbral = math.pi / 6  # 30 grados: por debajo de esto las aristas se ven amontonadas

        for v in self.vertices:
            (xv, yv) = estado_dic[v]
            # angulo (respecto al eje x) de cada arista que sale del vertice v
            angulos = []
            for u in self.adyacencia[v]:
                (xu, yu) = estado_dic[u]
                angulos.append(math.atan2(yu - yv, xu - xv))

            # penaliza cada par de aristas cuyo angulo entre si sea menor al umbral
            for (a1, a2) in itertools.combinations(angulos, 2):
                diferencia = abs(a1 - a2)
                if diferencia > math.pi:        # normaliza al menor angulo entre ambas
                    diferencia = 2 * math.pi - diferencia
                if diferencia < umbral:
                    total += (umbral - diferencia) / umbral
        return total

    def criterio_propio(self, estado_dic):
        """
        Implementa y comenta correctamente un criterio de costo que sea
        conveniente para que un grafo luzca bien.

        @param estado_dic: Diccionario cuyas llaves son los vértices
                           del grafo y cuyos valores es una tupla con
                           la posición (x, y) de ese vértice en el
                           dibujo.

        @return: Un número.

        """
        # Criterio: penaliza que las aristas tengan longitudes muy dispares.
        # Un grafo se ve más ordenado y "limpio" cuando las aristas tienen
        # longitudes parecidas, así que se penaliza la desviación de cada
        # arista respecto a la longitud promedio (varianza normalizada).
        if not self.aristas:
            return 0.0

        longitudes = []
        for (v1, v2) in self.aristas:
            (x1, y1), (x2, y2) = estado_dic[v1], estado_dic[v2]
            longitudes.append(math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2))

        promedio = sum(longitudes) / len(longitudes)
        if promedio == 0:
            return 0.0
        varianza = sum((L - promedio) ** 2 for L in longitudes) / len(longitudes)
        return varianza / (promedio ** 2)  # coeficiente de variación al cuadrado

    def estado2dic(self, estado):
        """
        Convierte el estado en forma de tupla a un estado en forma
        de diccionario

        @param: Una tupla con las posiciones (x1, y1, x2, y2, ...)

        @return: Un diccionario cuyas llaves son el nombre de cada
                 arista y su valor es una tupla (x, y)

        """
        return {self.vertices[i]: (estado[2 * i], estado[2 * i + 1])
                for i in range(len(self.vertices))}

    def dibuja_grafo(self, estado=None, filename="prueba.gif"):
        """
        Dibuja el grafo utilizando el modulo pillow, donde estado es una
        lista de dimensión 2*len(vertices), donde cada valor es la
        posición en x y y respectivamente de cada vertice. dim es la
        dimensión de la figura en pixeles.

        Si no existe una posición, entonces se obtiene una en forma
        aleatoria.

        """
        if not estado:
            estado = self.estado_aleatorio()

        # Diccionario donde lugar[vertice] = (posX, posY)
        lugar = self.estado2dic(estado)

        # Abre una imagen y para dibujar en la imagen
        # Imagen en blanco
        imagen = Image.new('RGB', (self.dim, self.dim), (255, 255, 255))
        dibujar = ImageDraw.ImageDraw(imagen)

        for (v1, v2) in self.aristas:
            dibujar.line((lugar[v1], lugar[v2]), fill=(255, 0, 0))
        for v in self.vertices:
            dibujar.text(lugar[v], v, (0, 0, 0))

        imagen.save(filename)


def calendarizador_geometrico(T_ini, alfa=0.95, n=int(1e10)):
    """
    Calendarización geométrica: T_{k+1} = alfa * T_k, con 0 < alfa < 1.

    A diferencia de la calendarización por default (T_ini/(1+i), que baja muy
    rápido al inicio y muy lento al final), la geométrica mantiene una bajada
    proporcional constante, lo que acopla mejor con un vecino de paso gaussiano:
    da más tiempo de exploración a temperatura media.

    @param T_ini: Temperatura inicial.
    @param alfa: Factor de enfriamiento (más cercano a 1 = más lento).
    @return: Un generador de temperaturas.
    """
    T = T_ini
    for _ in range(n):
        yield T
        T *= alfa


def main():
    """
    La función principal

    """

    # Vamos a definir un grafo sencillo
    vertices_sencillo = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    aristas_sencillo = [('B', 'G'),
                        ('E', 'F'),
                        ('H', 'E'),
                        ('D', 'B'),
                        ('H', 'G'),
                        ('A', 'E'),
                        ('C', 'F'),
                        ('H', 'B'),
                        ('F', 'A'),
                        ('C', 'B'),
                        ('H', 'F')]
    dimension = 400

    # Y vamos a hacer un dibujo del grafo sin decirle como hacer para
    # ajustarlo.
    grafo_sencillo = problema_grafica_grafo(vertices_sencillo,
                                            aristas_sencillo,
                                            dimension)

    estado_aleatorio = grafo_sencillo.estado_aleatorio()
    costo_inicial = grafo_sencillo.costo(estado_aleatorio)
    grafo_sencillo.dibuja_grafo(estado_aleatorio, "prueba_inicial.gif")
    print("Costo del estado aleatorio: {}".format(costo_inicial))

    # Ahora vamos a encontrar donde deben de estar los puntos, usando la
    # calendarización geométrica acoplada al vecino gaussiano.
    t_inicial = time.time()
    T_ini = 5 * grafo_sencillo.costo(grafo_sencillo.estado_aleatorio()) + 100
    calendario = calendarizador_geometrico(T_ini, alfa=0.99)
    solucion = blocales.temple_simulado(grafo_sencillo, calendario)
    t_final = time.time()
    costo_final = grafo_sencillo.costo(solucion)

    grafo_sencillo.dibuja_grafo(solucion, "prueba_final.gif")
    print("\nUtilizando la calendarización geométrica")
    print("Costo de la solución encontrada: {}".format(costo_final))
    print("Tiempo de ejecución en segundos: {}".format(t_final - t_inicial))

    # Un grafo "más feo": denso y propenso a cruces (grafo bipartito K(3,3),
    # que no es planar, más algunas aristas extra para complicarlo).
    vertices_feo = ['1', '2', '3', '4', '5', '6']
    aristas_feo = [('1', '4'), ('1', '5'), ('1', '6'),
                   ('2', '4'), ('2', '5'), ('2', '6'),
                   ('3', '4'), ('3', '5'), ('3', '6')]
    grafo_feo = problema_grafica_grafo(vertices_feo, aristas_feo, dimension)

    inicial_feo = grafo_feo.estado_aleatorio()
    grafo_feo.dibuja_grafo(inicial_feo, "feo_inicial.gif")
    print("\nGrafo feo - costo inicial: {}".format(grafo_feo.costo(inicial_feo)))

    T_ini_feo = 5 * grafo_feo.costo(grafo_feo.estado_aleatorio()) + 100
    cal_feo = calendarizador_geometrico(T_ini_feo, alfa=0.99)
    sol_feo = blocales.temple_simulado(grafo_feo, cal_feo)
    grafo_feo.dibuja_grafo(sol_feo, "feo_final.gif")
    print("Grafo feo - costo final: {}".format(grafo_feo.costo(sol_feo)))


if __name__ == '__main__':
    main()