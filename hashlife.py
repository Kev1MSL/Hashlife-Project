#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thur April 15 08:57:12 2021

@author: kevin and marten
"""

import math
import weakref

GROUP = [
    "kevin.messali@polytechnique.edu",
    "riho.pallum@polytechnique.edu",
]


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
nodes = weakref.WeakValueDictionary()


class AbstractNode:
    BIG = False  # The value is ignored

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
        if k == 0:
            return AbstractNode.cell(False)
        else:
            zero = AbstractNode.zero(k - 1);
            return AbstractNode.node(nw=zero, ne=zero, sw=zero, se=zero)

    ####################################################################################################################
    #                                           Question 3                                                             #
    ####################################################################################################################

    def extend(self):
        if self.level == 0:
            empty = AbstractNode.cell(False);
            return AbstractNode.node(empty, AbstractNode.cell(self.alive), empty, empty)
        zero = AbstractNode.zero(self.level - 1);
        return AbstractNode.node(
            AbstractNode.node(zero, zero, zero, self.nw),
            AbstractNode.node(zero, zero, self.ne, zero),
            AbstractNode.node(zero, self.sw, zero, zero),
            AbstractNode.node(self.se, zero, zero, zero))

    ####################################################################################################################
    #                                           Question 4 and 5                                                       #
    ####################################################################################################################

    def forward(self):
        if self.population == 0:
            return AbstractNode.zero(self.level - 1)
        if self._cache is not None:
            return self._cache
        if self.level < 2:
            return None
        if self.level == 2:
            cells = [
                self.se.se.alive, self.se.sw.alive, self.sw.se.alive, self.sw.sw.alive,
                self.se.ne.alive, self.se.nw.alive, self.sw.ne.alive, self.sw.nw.alive,
                self.ne.se.alive, self.ne.sw.alive, self.nw.se.alive, self.nw.sw.alive,
                self.ne.ne.alive, self.ne.nw.alive, self.nw.ne.alive, self.nw.nw.alive]
            w = 0
            for i in range(len(cells) - 1, -1, -1):
                w = w | (int(cells[i]) << i)
            self._cache = Node.level2_bitmask(w)

        if self.level > 2:
            q_nw, q_tc, q_ne, q_cl, q_cc, q_cr, q_sw, q_bc, q_se = self._quadrant_builder()
            r_nw, r_tc, r_ne, r_cl, r_cc, r_cr, r_sw, r_bc, r_se = q_nw.forward(), \
                                                                   q_tc.forward(), \
                                                                   q_ne.forward(), \
                                                                   q_cl.forward(), \
                                                                   q_cc.forward(), \
                                                                   q_cr.forward(), \
                                                                   q_sw.forward(), \
                                                                   q_bc.forward(), \
                                                                   q_se.forward()

            a_nw, a_ne, a_sw, a_se = self._a_builder(r_nw, r_tc, r_ne, r_cl, r_cc, r_cr, r_sw, r_bc, r_se)
            b_nw, b_ne, b_sw, b_se = a_nw.forward(), \
                                     a_ne.forward(), \
                                     a_sw.forward(), \
                                     a_se.forward()
            self._cache = AbstractNode.node(nw=b_nw, ne=b_ne, sw=b_sw, se=b_se)
        return self._cache

    def _quadrant_builder(self):
        q_nw, q_ne, q_sw, q_se = self.nw, self.ne, self.sw, self.se
        q_tc = AbstractNode.node(nw=q_nw.ne, ne=q_ne.nw, sw=q_nw.se, se=q_ne.sw)
        q_cl = AbstractNode.node(nw=q_nw.sw, ne=q_nw.se, sw=q_sw.nw, se=q_sw.ne)
        q_cc = AbstractNode.node(nw=q_nw.se, ne=q_ne.sw, sw=q_sw.ne, se=q_se.nw)
        q_cr = AbstractNode.node(nw=q_ne.sw, ne=q_ne.se, sw=q_se.nw, se=q_se.ne)
        q_bc = AbstractNode.node(nw=q_sw.ne, ne=q_se.nw, sw=q_sw.se, se=q_se.sw)
        return q_nw, q_tc, q_ne, q_cl, q_cc, q_cr, q_sw, q_bc, q_se

    def _a_builder(self, r_nw, r_tc, r_ne, r_cl, r_cc, r_cr, r_sw, r_bc, r_se):
        a_nw = AbstractNode.node(nw=r_nw, ne=r_tc, sw=r_cl, se=r_cc)
        a_ne = AbstractNode.node(nw=r_tc, ne=r_ne, sw=r_cc, se=r_cr)
        a_sw = AbstractNode.node(nw=r_cl, ne=r_cc, sw=r_sw, se=r_bc)
        a_se = AbstractNode.node(nw=r_cc, ne=r_cr, sw=r_bc, se=r_se)
        return a_nw, a_ne, a_sw, a_se

        # if self not in self._cache:
        #     if self.level < 2:
        #         self._cache[self] = None
        #         print("level < 2")
        #         # return None
        #
        #     if self.level == 2:
        #         NaiveUniverse(4, 4, self).round()
        #         self._cache[self] = AbstractNode.node(self.nw, self.ne, self.sw, self.se)
        #         print("level = 2")
        #         # return NaiveUniverse(4, 4, self).round()
        #
        #     if self.level > 2:
        #         q_nw, q_ne, q_sw, q_se = self.nw, self.ne, self.sw, self.se
        #         self._cache[self] = AbstractNode.node(q_nw.se, q_ne.sw, q_sw.ne, q_se.nw)
        #         print("level > 2", self._cache)
        #         # return Node(q_nw.se, q_ne.sw, q_sw.ne, q_se.nw)
        # return self._cache[self]

    ####################################################################################################################
    #                                           Question 6                                                             #
    ####################################################################################################################

    @staticmethod
    def canon(node):
        return nodes.setdefault(node, node)

    ####################################################################################################################
    #                                           Question 7                                                             #
    ####################################################################################################################

    @staticmethod
    def cell(alive):
        return AbstractNode.canon(CellNode(alive))
        # return CellNode(alive)

    @staticmethod
    def node(nw, ne, sw, se):
        return AbstractNode.canon(Node(nw, ne, sw, se))
        # return Node(nw, ne, sw, se)

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

    @staticmethod
    def level2_bitmask(mask):
        # We have:
        # mask_e_5 = 0b11101010111
        # mask_e_6 = 0b111010101110
        # mask_e_9 = 0b111010101110000
        # mask_e_10 = 1110101011100000
        # Therefore from mask_e_5 we can determine the others:
        mask_e_5 = 0b11101010111
        mask_e_6 = mask_e_5 << 1
        mask_e_9 = mask_e_6 << 3
        mask_e_10 = mask_e_9 << 1
        nw = 1 \
            if (Node.bit_counter(mask & mask_e_10) == 3 and Node.bit_alive(mask, 10) == 0) or \
               (Node.bit_counter(mask & mask_e_10) in [2, 3] and Node.bit_alive(mask, 10) == 1) \
            else 0
        ne = 1 \
            if (Node.bit_counter(mask & mask_e_9) == 3 and Node.bit_alive(mask, 9) == 0) or \
               (Node.bit_counter(mask & mask_e_9) in [2, 3] and Node.bit_alive(mask, 9) == 1) \
            else 0
        sw = 1 \
            if (Node.bit_counter(mask & mask_e_6) == 3 and Node.bit_alive(mask, 6) == 0) or \
               (Node.bit_counter(mask & mask_e_6) in [2, 3] and Node.bit_alive(mask, 6) == 1) \
            else 0
        se = 1 \
            if (Node.bit_counter(mask & mask_e_5) == 3 and Node.bit_alive(mask, 5) == 0) or \
               (Node.bit_counter(mask & mask_e_5) in [2, 3] and Node.bit_alive(mask, 5) == 1) \
            else 0
        return AbstractNode.node(
            nw=AbstractNode.cell(nw),
            ne=AbstractNode.cell(ne),
            sw=AbstractNode.cell(sw),
            se=AbstractNode.cell(se))

    @staticmethod
    def bit_counter(mask):
        if mask == 0:
            return 0
        i = 0
        while mask != 0:
            mask = mask & (mask - 1)
            i += 1
        return i

    @staticmethod
    def bit_alive(mask, i):
        """ Return 1 or 0 depending on whether the ith-least significant bit
                of x is 1 or 0.
            """
        return 0 if mask & (1 << i) == 0 else 1

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
        return AbstractNode.node(AbstractNode.cell(False), AbstractNode.cell(False), AbstractNode.cell(False),
                                 AbstractNode.cell(False))

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


