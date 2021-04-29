#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thur April 15 08:57:12 2021

@author: kevin and marten
"""


class Universe:
    def round(self):
        """Compute (in place) the next generation of the universe"""
        raise NotImplementedError

    def get(self, i, j):
        """Returns the state of the cell at coordinates (ij[0], ij[1])"""
        raise NotImplementedError

    def rounds(self, n):
        """Compute (in place) the n-th next generation of the universe"""
        for _i in range(n):
            self.round()


class NaiveUniverse(Universe):
    def __init__(self, n, m, cells):
        self.n = n
        self.m = m
        self.__cells = cells

    def repr(self):
        s = ""
        for i in range(self.n):
            for j in range(self.m):
                if self.get(self.n - i - 1, j):
                    s += "1 "
                else:
                    s += "0 "
            s += "\n"
        return s

    def get(self, i, j):
        return self.__cells[i][j]

    def round(self):
        next_round_cells = [sub[:] for sub in self.__cells]
        for i in range(self.n):
            for j in range(self.m):
                n_neighbors = len(self.get_living_neighbors(i, j))
                is_alive = self.get(i, j)
                if not is_alive and n_neighbors == 3:
                    next_round_cells[i][j] = True
                elif is_alive and n_neighbors in [2, 3]:
                    next_round_cells[i][j] = True
                else:
                    next_round_cells[i][j] = False
        self.__cells = next_round_cells

    def get_living_neighbors(self, i, j):
        neighbors = list()
        for i_pointer in range(i - 1, i + 2):
            for j_pointer in range(j - 1, j + 2):
                if 0 <= i_pointer < self.n and 0 <= j_pointer < self.n and (
                        i_pointer != i or j_pointer != j) and self.get(i_pointer, j_pointer):
                    neighbors.append((i_pointer, j_pointer))
        return neighbors
