#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thur April 15 08:57:12 2021

@author: kevin and marten
"""

import math


########################################################################################################################
#                                           Question 1                                                                 #
########################################################################################################################
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
                if 0 <= i_pointer < self.n and 0 <= j_pointer < self.m and (
                        i_pointer != i or j_pointer != j) and self.get(i_pointer, j_pointer):
                    neighbors.append((i_pointer, j_pointer))
        return neighbors


########################################################################################################################
#                                           Question 2, 3, 4, 5 and 6                                                  #
########################################################################################################################
nodes = dict()


class AbstractNode:

    ####################################################################################################################
    #                                           Question 5 and 6                                                       #
    ####################################################################################################################
    def __init__(self):
        self._cache = None
        self._hash = None

    ####################################################################################################################
    #                                           Question 6                                                             #
    ####################################################################################################################
    def __hash__(self):
        if self._hash is None:
            self._hash = (
                self.population,
                self.level,
                self.nw,
                self.ne,
                self.sw,
                self.se,
            )
            self._hash = hash(self._hash)
        return self._hash

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, AbstractNode):
            return False
        return \
            self.level == other.level and \
            self.population == other.population and \
            self.nw is other.nw and \
            self.ne is other.ne and \
            self.sw is other.sw and \
            self.se is other.se

    @property
    def level(self):
        """Level of this node"""
        raise NotImplementedError

    @property
    def population(self):
        """Total population of the area"""
        raise NotImplementedError

    ####################################################################################################################
    #                                           Question 2                                                             #
    ####################################################################################################################

    @staticmethod
    def zero(k):
        def _zero(i, x, y):
            if i == 0:
                return CellNode(False)
            h = 2 ** (i - 1)
            nw = _zero(i - 1, x, y)
            ne = _zero(i - 1, x, y + h)
            sw = _zero(i - 1, x + h, y)
            se = _zero(i - 1, x + h, y + h)
            return Node(nw, ne, sw, se)

        return _zero(k, 0, 0)

    ####################################################################################################################
    #                                           Question 3                                                             #
    ####################################################################################################################

    def extend(self):
        if self.level == 0:
            return Node(CellNode(False), self, CellNode(False), CellNode(False))
        return Node(
            Node(self.zero(self.level - 1), self.zero(self.level - 1), self.zero(self.level - 1), self.nw),
            Node(self.zero(self.level - 1), self.zero(self.level - 1), self.ne, self.zero(self.level - 1)),
            Node(self.zero(self.level - 1), self.sw, self.zero(self.level - 1), self.zero(self.level - 1)),
            Node(self.se, self.zero(self.level - 1), self.zero(self.level - 1), self.zero(self.level - 1)))

    ####################################################################################################################
    #                                           Question 4 and 5                                                       #
    ####################################################################################################################

    def forward(self):
        self._cache = dict() if self._cache is None else self._cache

        if self not in self._cache:
            if self.level < 2:
                self._cache[self] = None
                # return None

            if self.level == 2:
                NaiveUniverse(4, 4, self).round()
                self._cache[self] = self
                # return NaiveUniverse(4, 4, self).round()

            if self.level > 2:
                q_nw, q_ne, q_sw, q_se = self.nw, self.ne, self.sw, self.se
                self._cache[self] = Node(q_nw.se, q_ne.sw, q_sw.ne, q_se.nw)
                # return Node(q_nw.se, q_ne.sw, q_sw.ne, q_se.nw)

        return self._cache[self]

        # return Node(q_nw.se, q_ne.sw, q_sw.ne, q_se.nw)
        # q_tc, q_bc, q_cl, q_cr, q_cc = self.quad_cv(q_nw, q_ne), \
        #                                self.quad_cv(q_sw, q_se), \
        #                                self.quad_ch(q_nw, q_sw), \
        #                                self.quad_ch(q_ne, q_se), \
        #                                Node(q_nw.se, q_ne.sw, q_sw.ne, q_se.nw)

        # r_nw = self.central_area(q_nw)
        # r_ne = self.central_area(q_ne)
        # r_sw = self.central_area(q_sw)
        # r_se = self.central_area(q_se)
        # r_tc = self.central_area(q_tc)
        # r_bc = self.central_area(q_bc)
        # r_cl = self.central_area(q_cl)
        # r_cr = self.central_area(q_cr)
        # r_cc = self.central_area(q_cc)
        #
        #
        # a_nw = Node(r_nw, r_tc, r_cl, r_cc)
        # # b_nw = q_cc.nw
        # a_ne = Node(r_tc, r_ne, r_cc, r_cr)
        # # b_ne = q_cc.ne
        # a_sw = Node(r_cl, r_cc, r_sw, r_bc)
        # # b_sw = q_cc.sw
        # a_se = Node(r_cc, r_cr, r_bc, r_se)
        # # b_se = q_cc.se
        # return q_cc

    # def central_area(self, q_tree):
    #     return Node(q_tree.nw.se, q_tree.ne.sw, q_tree.sw.ne, q_tree.se.nw)
    #
    # def quad_cv(self, q_left, q_right):
    #     """
    #     Compute the quad tree area of the one on the vertical axis.
    #     :param q_left:
    #     :param q_right:
    #     :return:
    #     """
    #     return Node(q_left.ne, q_right.nw, q_left.se, q_right.sw)
    #
    # def quad_ch(self, q_top, q_bottom):
    #     """
    #     Compute the quad tree area of the one on the horizontal axis.
    #     :param q_top:
    #     :param q_bottom:
    #     :return:
    #     """
    #     return Node(q_top.sw, q_top.se, q_bottom.nw, q_bottom.ne)

    ####################################################################################################################
    #                                           Question 6                                                             #
    ####################################################################################################################

    @staticmethod
    def canon(node):
        # if node in nodes:
        #     return nodes[node]
        # nodes[node] = node
        for n in nodes:
            if n == node:
                return nodes[node]
        nodes[node] = node

    ####################################################################################################################
    #                                           Question 7                                                             #
    ####################################################################################################################

    @staticmethod
    def cell(alive):
        return CellNode(alive)

    @staticmethod
    def node(nw, ne, sw, se):
        return Node(nw, ne, sw, se)

    nw = property(lambda self: None)
    ne = property(lambda self: None)
    sw = property(lambda self: None)
    se = property(lambda self: None)


class CellNode(AbstractNode):
    def __init__(self, alive):
        super().__init__()

        self._alive = bool(alive)

    level = property(lambda self: 0)
    population = property(lambda self: int(self._alive))
    alive = property(lambda self: self._alive)


class Node(AbstractNode):
    def __init__(self, nw, ne, sw, se):
        super().__init__()

        self._level = 1 + nw.level
        self._population = \
            nw.population + \
            ne.population + \
            sw.population + \
            se.population
        self._nw = nw
        self._ne = ne
        self._sw = sw
        self._se = se

    level = property(lambda self: self._level)
    population = property(lambda self: self._population)

    nw = property(lambda self: self._nw)
    ne = property(lambda self: self._ne)
    sw = property(lambda self: self._sw)
    se = property(lambda self: self._se)


class HashLifeUniverse(Universe):
    def __init__(self, *args):
        if len(args) == 1:
            self._root = args[0]
        else:
            self._root = HashLifeUniverse.load(*args)

        self._generation = 0

    @staticmethod
    def load(n, m, cells):
        level = math.ceil(math.log(max(1, n, m), 2))

        mkcell = getattr(AbstractNode, 'cell', CellNode)
        mknode = getattr(AbstractNode, 'node', Node)

        def get(i, j):
            i, j = i + n // 2, j + m // 2
            return \
                i in range(n) and \
                j in range(m) and \
                cells[i][j]

        def create(i, j, level):
            if level == 0:
                return mkcell(get(i, j))

            noffset = 1 if level < 2 else 1 << (level - 2)
            poffset = 0 if level < 2 else 1 << (level - 2)

            nw = create(i - noffset, j + poffset, level - 1)
            sw = create(i - noffset, j - noffset, level - 1)
            ne = create(i + poffset, j + poffset, level - 1)
            se = create(i + poffset, j - noffset, level - 1)

            return mknode(nw=nw, ne=ne, sw=sw, se=se)

        return create(0, 0, level)

    def get(self, i, j):
        # Do something here
        raise NotImplementedError()

    def rounds(self, n):
        # Do something here
        raise NotImplementedError()

    def round(self):
        return self.rounds(1)

    @property
    def root(self):
        return self._root

    @property
    def generation(self):
        return self._generation
