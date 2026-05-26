#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
genetico_tarea.py
-----------------

En este módulo vas a desarrollar tu propio algoritmo
genético para resolver problemas de permutaciones

"""

import random
import genetico

__author__ = 'Dante Alejandro Tostado Cortes'


class GeneticoPermutacionesPropio(genetico.Genetico):
    """
    Algoritmo genético para permutaciones, con las siguientes características:

    - Representación: código de Lehmer en vez de permutación directa. Cada
      gen i vive en el rango [0, n-1-i], así que cualquier cadena válida
      mapea a una permutación válida. Esto permite usar la cruza de un punto
      clásica sin necesidad de reparar.
    - Selección: por torneo en vez de ruleta.
    - Cruza: de un punto clásica en vez de la cruza de orden.
    - Mutación: intercambio (swap) de dos posiciones sobre la permutación
      decodificada. El swap da el ajuste fino que la representación Lehmer
      no logra mutando genes sueltos (cambiar un gen temprano reordena toda
      la permutación), recodificando el resultado de vuelta a Lehmer.
    - Reemplazo: steady-state (los hijos compiten contra la población
      completa y solo sobreviven los mejores) en vez de elitismo simple.

    """
    def __init__(self, problema, n_población, prob_muta=0.8, tam_torneo=3):
        """
        @param prob_muta: Probabilidad de mutación por individuo.
        @param tam_torneo: Número de individuos que compiten en cada torneo.

        """
        self.prob_muta = prob_muta
        self.tam_torneo = tam_torneo
        self.nombre = ('propuesto por el alumno (Lehmer + torneo, ' +
                       'prob. muta ' + str(prob_muta) + ')')
        super().__init__(problema, n_población)

    @staticmethod
    def estado_a_cadena(estado):
        """
        Convierte un estado (permutación) a su código de Lehmer.

        @param estado: Una tupla con un estado
        @return: Una lista con el código de Lehmer

        """
        # cadena[i] = cuántos elementos a la derecha de estado[i] son menores
        n = len(estado)
        return [sum(1 for j in range(i + 1, n) if estado[j] < estado[i])
                for i in range(n)]

    @staticmethod
    def cadena_a_estado(cadena):
        """
        Reconstruye la permutación a partir de su código de Lehmer.

        @param cadena: Una lista de cromosomas (código de Lehmer)
        @return: Una tupla con un estado válido

        """
        disponibles = list(range(len(cadena)))
        return tuple(disponibles.pop(c) for c in cadena)

    def adaptación(self, individuo):
        """
        Adaptación inversamente proporcional al costo. Mientras menos
        conflictos, mayor adaptación.

        @param individuo: Una lista de cromosomas
        @return: Un número con la adaptación del individuo

        """
        costo = self.problema.costo(self.cadena_a_estado(individuo))
        return 1.0 / (1.0 + costo)

    def selección(self):
        """
        Selección por torneo: para cada pareja se eligen tam_torneo
        individuos al azar y gana el de mayor adaptación.

        @return: Una lista de pares de índices a cruzar

        """
        return [(self._torneo(), self._torneo())
                for _ in range(self.n_población)]

    def _torneo(self):
        """
        Un torneo: toma tam_torneo competidores al azar y regresa el
        índice del de mayor adaptación.

        """
        competidores = random.sample(range(self.n_población),
                                      min(self.tam_torneo, self.n_población))
        return max(competidores, key=lambda i: self.población[i][0])

    def cruza_individual(self, cadena1, cadena2):
        """
        Cruza de un punto clásica. Como la representación de Lehmer hace
        válida cualquier cadena, no se necesita reparación.

        @param cadena1: Una lista de cromosomas
        @param cadena2: Una lista de cromosomas
        @return: Un individuo nuevo

        """
        corte = random.randint(1, len(cadena1) - 1)
        return cadena1[:corte] + cadena2[corte:]

    def mutación(self, individuos):
        """
        Mutación por intercambio: con probabilidad prob_muta se decodifica
        el individuo a permutación, se intercambian dos posiciones al azar y
        se recodifica a Lehmer. El swap actúa sobre la permutación, que es
        donde el cambio tiene un efecto local y controlado.

        @param individuos: Una lista de individuos (listas)
        @return: None (muta en su lugar)

        """
        for individuo in individuos:
            if random.random() < self.prob_muta:
                perm = list(self.cadena_a_estado(individuo))
                i, j = random.sample(range(len(perm)), 2)
                perm[i], perm[j] = perm[j], perm[i]
                individuo[:] = self.estado_a_cadena(tuple(perm))

    def reemplazo_generacional(self, individuos):
        """
        Reemplazo steady-state: se juntan padres e hijos y sobreviven los
        n_población mejores. Conserva la mejor solución sin descartar de
        golpe a toda la generación anterior.

        @param individuos: Lista de cromosomas de hijos
        @return: None (cambia self.población internamente)

        """
        hijos = [(self.adaptación(ind), ind) for ind in individuos]
        combinada = self.población + hijos
        combinada.sort(key=lambda par: par[0], reverse=True)
        self.población = combinada[:self.n_población]


if __name__ == "__main__":
    # Un objeto genético con permutaciones con una población de
    # 10 individuos y una probabilidad de mutacion de 0.1
    g_propio = GeneticoPermutacionesPropio(genetico.ProblemaTonto(10), 10)
    genetico.prueba(g_propio)