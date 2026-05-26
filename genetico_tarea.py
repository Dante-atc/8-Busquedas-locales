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
    Clase con un algoritmo genético adaptado a problemas de permutaciones

    """
    def __init__(self, problema, n_población):
        """
        Aqui puedes poner algunos de los parámetros
        que quieras utilizar en tu clase

        Para esta tarea vamos a cambiar la forma de representación
        para que se puedan utilizar operadores clásicos (esto implica
        reescribir los métodos estáticos cadea_a_estado y
        estado_a_cadena).

        """
        self.nombre = 'Algoritmo Genetico del Politico Corrupto'
        #
        # ------ IMPLEMENTA AQUI TU CÓDIGO -----------------------------------
        #
        # Parametros tematicos:
        #   prob_chapulineo : probabilidad de que un politico "chapulinee"
        #                     (cambie de puesto por conveniencia) -> mutacion.
        #   tam_casta       : cuantos poderosos de la "vieja guardia" se
        #                     aferran al poder cada generacion -> reemplazo.
        self.prob_chapulineo = 0.3
        self.tam_casta = max(1, n_población // 25)
        super().__init__(problema, n_población)

    @staticmethod
    def estado_a_cadena(estado):
        """
        Convierte un estado a una cadena de cromosomas independiente
        del problema de permutación

        @param estado: Una tupla con un estado
        @return: Una lista con una cadena de caracteres

        """
        #
        # ------ IMPLEMENTA AQUI TU CÓDIGO --------------------------------
        #
        # Representacion: "expediente de sobornos" (codigo de Lehmer). Cada
        # gen i cuenta cuantos puestos a la derecha valen menos que el actual.
        # Cualquier expediente valido mapea a una permutacion valida, asi que
        # los acuerdos turbios (cruza) nunca producen un gabinete imposible.
        n = len(estado)
        return [sum(1 for j in range(i + 1, n) if estado[j] < estado[i])
                for i in range(n)]

    @staticmethod
    def cadena_a_estado(cadena):
        """
        Convierte una cadena de cromosomas a un estado donde el estado es
        una posible solución a un problema de permutaciones

        @param cadena: Una lista de cromosomas o valores
        @return: Una tupla con un estado válido

        """
        #
        # ------ IMPLEMENTA AQUI TU CÓDIGO --------------------------------
        #
        # Reconstruye el gabinete (permutacion) a partir del expediente.
        disponibles = list(range(len(cadena)))
        return tuple(disponibles.pop(c) for c in cadena)

        
    def adaptación(self, individuo):
        """
        Calcula la adaptación de un individuo al medio, mientras más adaptado
        mejor, mayor costo, menor adaptción.

        @param individuo: Una lista de cromosomas
        @return un número con la adaptación del individuo

        """
        #
        # ------ IMPLEMENTA AQUI TU CÓDIGO --------------------------------
        #
        # "Nivel de poder" del politico: a menos conflictos (menos escandalos),
        # mas poder acumula. Inversamente proporcional al costo.
        costo = self.problema.costo(self.cadena_a_estado(individuo))
        return 1.0 / (1.0 + costo)

    def selección(self):
        """
        Seleccion de estados mediante método diferente a la ruleta

        @return: Una lista con pares de indices de los individuo que se van
                 a cruzar

        """
        #
        # ------ IMPLEMENTA AQUI TU CÓDIGO ----------------------------------
        #
        # "Compra de votos": No como ruleta. Se ordena a los politicos por poder
        # (ranking) y se elige sesgando fuertemente hacia los mas poderosos:
        # con r = random()**2 (r en [0,1) pero apilado cerca de 0) siempre se
        # escogen indices del tope del ranking. Los ricos compran su lugar.
        ranking = sorted(range(self.n_población),
                         key=lambda i: self.población[i][0],
                         reverse=True)

        def compra_voto():
            # Sesgo lineal hacia los poderosos: se eligen dos al azar y gana
            # el mejor situado en el ranking (el mas rico compra el voto). Es
            # mas suave que un sesgo cuadratico, asi los menos poderosos aun
            # entran de vez en cuando y la diversidad no colapsa de golpe.
            a, b = random.randrange(self.n_población), random.randrange(self.n_población)
            return ranking[min(a, b)]

        return [(compra_voto(), compra_voto())
                for _ in range(self.n_población)]

    def cruza_individual(self, cadena1, cadena2):
        """
        @param cadena1: Una tupla con un individuo
        @param cadena2: Una tupla con otro individuo
        @return: Un individuo

        """
        #
        # ------ IMPLEMENTA AQUI TU CÓDIGO ----------------------------------
        #
        # "Acuerdo bajo la mesa": cruza de un punto. El hijo (el heredero
        # politico) se queda con la primera mitad del expediente del primer
        # padrino y el resto se lo arregla el segundo. Como es codigo de
        # Lehmer, el gabinete resultante siempre es valido (sin reparar).
        corte = random.randint(1, len(cadena1) - 1)
        return cadena1[:corte] + cadena2[corte:]

    def mutación(self, individuos):
        """

        @param poblacion: Una lista de individuos (listas).

        @return: None, es efecto colateral mutando los individuos
                 en la misma lista

        """
        #
        # ------ IMPLEMENTA AQUI TU CÓDIGO --------------------------------
        #
        # "Chapulineo": con probabilidad prob_chapulineo el politico brinca
        # de un puesto a otro por pura conveniencia (intercambio de dos
        # posiciones en el gabinete). Se hace sobre la permutacion decodificada
        # y se vuelve a codificar, porque ahi el brinco tiene efecto local.
        for individuo in individuos:
            if random.random() < self.prob_chapulineo:
                gabinete = list(self.cadena_a_estado(individuo))
                i, j = random.sample(range(len(gabinete)), 2)
                gabinete[i], gabinete[j] = gabinete[j], gabinete[i]
                individuo[:] = self.estado_a_cadena(tuple(gabinete))

    def reemplazo_generacional(self, individuos):
        """
        Realiza el reemplazo generacional diferente al elitismo

        @param individuos: Una lista de cromosomas de hijos que pueden
                           usarse en el reemplazo
        @return: None (todo lo cambia internamente)

        Por default usamos solo el elitismo de conservar al mejor, solo si es
        mejor que lo que hemos encontrado hasta el momento.

        """
        #
        # ------ IMPLEMENTA AQUI TU CÓDIGO --------------------------------
        #
        # "La casta nunca se va": en vez del elitismo simple (que solo salva al
        # #1), aqui una casta completa de los tam_casta politicos mas poderosos
        # se aferra al poder pase lo que pase. Los lugares restantes se llenan
        # con los hijos (la nueva camada de juniors) mejor adaptados.
        casta = sorted(self.población, key=lambda par: par[0],
                       reverse=True)[:self.tam_casta]

        camada = [(self.adaptación(ind), ind) for ind in individuos]
        camada.sort(key=lambda par: par[0], reverse=True)

        nueva = casta + camada[:self.n_población - self.tam_casta]

        # "Fiscal anticorrupcion": si el sistema se vuelve demasiado homogeneo
        # (todos clones de los mismos corruptos), interviene el fiscal y mete
        # ciudadanos nuevos al azar para romper la red de complicidad. Se mide
        # la diversidad como la fraccion de expedientes distintos; si cae por
        # debajo del umbral, se reemplaza al peor tercio con sangre nueva.
        distintos = len({tuple(ind) for (_, ind) in nueva})
        if distintos < 0.7 * self.n_población:
            n_nuevos = self.n_población // 2
            nueva.sort(key=lambda par: par[0], reverse=True)
            for k in range(n_nuevos):
                ciudadano = self.estado_a_cadena(
                    self.problema.estado_aleatorio())
                nueva[-(k + 1)] = (self.adaptación(ciudadano), ciudadano)

        self.población = nueva


if __name__ == "__main__":
    # Un objeto genético con permutaciones con una población de
    # 10 individuos y una probabilidad de mutacion de 0.1
    g_propio = GeneticoPermutacionesPropio(genetico.ProblemaTonto(10), 10)
    genetico.prueba(g_propio)



# Resultado en consola:
#El estado 8 se reproduce con el estado 3
#El estado 0 se reproduce con el estado 3
#
#Los mejores se espera se reproduzcan más
#
#Y para observar la cruza tenemos:
#progenitor 1: [1, 7, 4, 1, 4, 0, 1, 1, 1, 0]
#progenitor 2: [4, 4, 4, 1, 0, 3, 1, 0, 0, 0]
#descendiente: [1, 7, 4, 1, 0, 3, 1, 0, 0, 0]
#Haciendo una cruza de todas las parejas tenemos que:
#0: [1, 7, 4, 1, 0, 3, 1, 0, 0, 0]
#1: [0, 4, 0, 6, 2, 3, 0, 0, 1, 0]
#2: [1, 7, 4, 1, 4, 1, 0, 1, 0, 0]
#3: [0, 1, 0, 6, 2, 3, 0, 0, 1, 0]
#4: [0, 4, 0, 2, 4, 0, 1, 1, 1, 0]
#5: [5, 1, 4, 2, 5, 1, 3, 0, 1, 0]
#6: [2, 7, 1, 0, 2, 3, 0, 2, 0, 0]
#7: [1, 7, 4, 1, 4, 0, 1, 1, 1, 0]
#8: [9, 0, 2, 0, 5, 1, 1, 0, 0, 0]
#9: [1, 7, 4, 1, 4, 0, 1, 1, 0, 0]
#Y después de la mutación tenemos:
#0: [1, 7, 4, 1, 0, 3, 1, 0, 0, 0]
#1: [0, 2, 0, 6, 1, 3, 0, 0, 1, 0]
#2: [1, 7, 4, 1, 4, 1, 0, 1, 0, 0]
#3: [0, 8, 0, 0, 2, 3, 0, 0, 1, 0]
#4: [0, 4, 0, 2, 4, 0, 1, 1, 1, 0]
#5: [5, 1, 4, 2, 5, 1, 3, 0, 1, 0]
#6: [2, 4, 1, 0, 4, 3, 0, 2, 0, 0]
#7: [1, 7, 4, 1, 4, 0, 1, 1, 1, 0]
#8: [9, 0, 2, 0, 5, 1, 1, 0, 0, 0]
#9: [1, 7, 4, 1, 4, 0, 1, 1, 0, 0]
#
#
#Si iteramos por 20 generaciones tenemos que
#el estado que encontramos con menor costo es:
#
#(1, 8, 9, 2, 5, 3, 7, 4, 6, 0)
#
#Que debería tener el 0 y el 1 a los extremos