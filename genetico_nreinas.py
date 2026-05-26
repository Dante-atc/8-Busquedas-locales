#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prueba de los algoritmos genéticos utilizando el problema
de las n-reinas para aprender a ajustarlos y probarlos.

"""

from time import time
from itertools import combinations
from random import shuffle
import genetico
import genetico_tarea

__author__ = 'Dante Alejandro Tostado Cortes'

class ProblemaNreinas(genetico.Problema):
    """
    Las N reinas para AG

    """
    def __init__(self, n=8):
        self.n = n

    def estado_aleatorio(self):
        estado = list(range(self.n))
        shuffle(estado)
        return tuple(estado)

    def costo(self, estado):
        """
        Calcula el costo de un estado por el número de conflictos entre reinas

        @param estado: Una tupla que describe un estado

        @return: Un valor numérico, mientras más pequeño, mejor es el estado.

        """
        return sum([1 for (i, j) in combinations(range(self.n), 2)
                    if abs(estado[i] - estado[j]) == abs(i - j)])


def prueba_genetico(algo_genetico, n_generaciones, verbose=False):
    """
    Prueba de los algoritmos genéticos con el problema de las n reinas
    desarrollado para búsquedas locales (tarea 2).

    @param algo_genetico: objeto de la clase genetico.Genetico
    @param n_generaciones: Generaciones (iteraciones) del algortimo
    @param verbose: True si quieres desplegar informacion básica
    @return: Un estado con la solucion (una permutacion de range(n)

    """
    t_inicial = time()
    solucion = algo_genetico.busqueda(n_generaciones)
    t_final = time()
    if verbose:
        print("\nUtilizando el AG: {}".format(algo_genetico.nombre))
        print("Con poblacion de dimensión {}".format(
            algo_genetico.n_población))
        print("Con {} generaciones".format(n_generaciones))
        print("Costo de la solución encontrada: {}".format(
            algo_genetico.problema.costo(solucion)))
        print("Tiempo de ejecución en segundos: {}".format(
            t_final - t_inicial))
    return solucion


if __name__ == "__main__":

    # Modifica los parámetro del algoritmo genetico que propuso el
    # profesor (el cual se conoce como genetico.GeneticoPermutaciones)
    # buscando que el algoritmo encuentre SIEMPRE una solución óptima,
    # utilizando el menor tiempo posible en promedio. Realiza esto
    # para las 8, 16, 32, 64 y 128 reinas.
    #
    # Lo que puedes modificar es el tamaño de la población, el número
    # de generaciones y/o la probabilidad de mutación.
    #
    # Recuerda que podrias automatizar el problema haciendo una
    # función que genere una tabla con las soluciones, o hazlo a mano
    # si eso ayuda a comprender mejor el algoritmo.
    #
    #   -- ¿Cuales son en cada caso los mejores valores?  (escribelos
    #       abajo de esta linea)
    #
    #       n     poblacion   generaciones   prob_mutacion
    #       8        50           100            0.05
    #       16       150          200            0.05
    #       32       300          300            0.03
    #       64       500          500            0.03
    #       128      800          800            0.02
    #
    #       (poblacion y generaciones crecen ~linealmente con n; la
    #        probabilidad de mutacion baja al crecer n para no destruir
    #        bloques buenos que ya tomo trabajo armar.)
    #
    #   -- ¿Que reglas podrías establecer para asignar valores segun
    #       tu experiencia?
    #
    #       1. Poblacion del orden de 10*n: suficiente diversidad inicial
    #          sin desperdiciar evaluaciones.
    #       2. Generaciones tambien ~10*n: el problema necesita mas pasos
    #          para refinar a mayor n.
    #       3. Mutacion inversamente proporcional a n (entre 0.02 y 0.05):
    #          a mayor n, mas baja, porque una mutacion agresiva rompe
    #          configuraciones parciales valiosas.

    n_poblacion = 150
    generaciones = 200
    prob_mutacion = 0.05

    alg_gen = genetico.GeneticoPermutaciones(ProblemaNreinas(16),
                                             n_poblacion, prob_mutacion)

    solucion = prueba_genetico(alg_gen, generaciones, True)

    # Modifica los parámetro del algoritmo genetico que propusite tu
    # mismo (el cual se conoce como
    # genetico_tarea.GeneticoPermutacionesPropio). De ser muchos
    # parámetros, restringete a 2 o 3, buscando que el algoritmo
    # encuentre SIEMPRE una solución óptima, utilizando el menor
    # tiempo posible en promedio. Realiza esto para las 8, 16, 32, 64 y 128
    # reinas.
    #
    #   -- ¿Cuales son en cada caso los mejores valores?
    #       (escribelos abajo de esta linea)
    #
    #       Mi AG es el "Algoritmo Genetico del Politico Corrupto". Su firma
    #       solo recibe (problema, poblacion); los demas parametros estan
    #       fijos dentro de la clase (prob_chapulineo=0.3, casta=poblacion/25).
    #       Lo unico que se ajusta es poblacion y generaciones:
    #
    #       n     poblacion   generaciones      exito
    #       8        50           200          siempre
    #       16       150          500          siempre
    #       32       250          600          casi siempre (~7/8)
    #       64       300          1000         siempre (~90 s)
    #       128      400          1500         resuelve (lento)
    #
    #   -- ¿Que reglas podrías establecer para asignar valores
    #       segun tu experiencia?
    #
    #       1. La poblacion escala ~10*n.
    #       2. Las generaciones tienen que crecer MAS rapido que en el AG del
    #          ejemplo, porque el "sistema corrupto" (casta aferrada +
    #          seleccion sesgada a los poderosos) explota muy bien al inicio
    #          pero le cuesta el ajuste fino: necesita muchas generaciones
    #          para que un "chapulineo" acierte el ultimo arreglo.
    #       3. El "fiscal anticorrupcion" (reinyeccion de diversidad) se
    #          dispara solo cuando la poblacion se vuelve homogenea; en la
    #          practica casi no entra porque la diversidad se mantiene alta.
    #
    #   Conclusion: el sistema corrupto es eficientisimo en problemas chicos,
    #   pero colapsa al escalar; entre mas grande el problema, mas le cuesta a la 
    #   casta soltar el poder para refinar la solucion. La representacion de
    #   Lehmer ademas converge mas lento que la permutacion directa.

    n_pob_propio = 150
    gen_propio = 500

    alg_propio = genetico_tarea.GeneticoPermutacionesPropio(
        ProblemaNreinas(16), n_pob_propio)

    solucion_propio = prueba_genetico(alg_propio, gen_propio, True)

    # Un ejemplo de ejecución de este código se encuentra aqui abajo:
    #Utilizando el AG: propuesto por Julio Waissmancon prob. de mutación 0.05
    #Con poblacion de dimensión 150
    #Con 200 generaciones
    #Costo de la solución encontrada: 0
    #Tiempo de ejecución en segundos: 0.5938417911529541
    #
    #Utilizando el AG: Algoritmo Genetico del Politico Corrupto
    #Con poblacion de dimensión 150
    #Con 500 generaciones
    #Costo de la solución encontrada: 0
    #Tiempo de ejecución en segundos: 1.4079899787902832