from vp import clockwise, Visibility


class PairDeque:
    # init
    def __init__(self):
        self.pairs = []
        self.head = 0
        self.tail = 0

    # build
    def push(self, a, b):
        if len(self.pairs) > 0 and a <= self.pairs[-1][0]:
            return
        while len(self.pairs) > 0 and b <= self.pairs[-1][1]:
            self.pairs.pop()
        self.pairs.append((a, b))

    def clear(self):
        self.pairs.clear()

    # query
    def head_size(self):
        return len(self.pairs) - self.head

    def head_a(self):
        return self.pairs[self.head][0]

    def head_b(self):
        return self.pairs[self.head][1]

    def head_next_b(self):
        return self.pairs[self.head + 1][1]

    def head_pop(self):
        self.head += 1

    def tail_size(self):
        return len(self.pairs) - self.tail

    def tail_a(self):
        return self.pairs[-1 - self.tail][0]

    def tail_b(self):
        return self.pairs[-1 - self.tail][1]

    def tail_prev_a(self):
        return self.pairs[-2 - self.tail][0]

    def tail_pop(self):
        self.tail += 1

    # reset
    def head_reset(self):
        self.head = 0

    def tail_reset(self):
        self.tail = 0


class Decomposition:
    def __init__(self, P):
        self._P = P
        n = len(P)

        # identify reflex vertices and build pointers to next reflex vertices
        self._is_reflex = [i == 0 or clockwise(P[i - 1], P[i], P[(i + 1) % n]) for i in range(n)]
        self._next_reflex = [None] * n
        for i in reversed(range(n)):
            self._next_reflex[i] = i + 1 if i == n - 1 or self._is_reflex[i + 1] else self._next_reflex[i + 1]

        # reorder vertices so that reflex vertices come first
        self._rx = [None] * n
        j = 0
        for i in range(n):
            if self._is_reflex[i]:
                self._rx[i] = j
                j += 1
        r = j
        for i in range(n):
            if not self._is_reflex[i]:
                self._rx[i] = j
                j += 1
        self._rx_weight = [[None] * (n if self._is_reflex[i] else r) for i in range(n)]
        self._rx_deque = [[None] * (n if self._is_reflex[i] else r) for i in range(n)]

        # initialize subproblems for valid diagonals
        for i in self._reflex_vertices(0, n):
            for k in Visibility(P, i).visible_vertices():
                if i < k - 1:  # diagonal (i, k) with i reflex
                    self._set_weight(i, k, n)  # set weight to n (valid)
                    self._new_deque(i, k)
                if k < i - 1 and not self._is_reflex[k]:  # diagonal (k, i) with k not reflex and i reflex
                    self._set_weight(k, i, n)  # set weight to n (valid)
                    self._new_deque(k, i)

        # dynamic programming
        for l in range(2, n):
            for i in self._reflex_vertices(0, n - l):
                k = i + l
                if self._is_visible(i, k):  # diagonal (i, k) with i reflex
                    if self._is_reflex[k]:
                        for j in range(i + 1, k):
                            self._head_scan(i, j, k)  # diagonal/edge (i, j) with i reflex, diagonal/edge (j, k) with k reflex
                    else:
                        for j in self._reflex_vertices(i + 1, k - 1):
                            self._head_scan(i, j, k)  # diagonal/edge (i, j) with i reflex and j reflex, diagonal (j, k) with j reflex and k not reflex
                        self._head_scan(i, k - 1, k)  # diagonal (i, k - 1) with i reflex, edge (k - 1, k)
            for k in self._reflex_vertices(l, n):
                i = k - l
                if not self._is_reflex[i] and self._is_visible(i, k):  # diagonal (i, k) with i not reflex and k reflex
                    self._tail_scan(i, i + 1, k)  # edge (i, i + 1), diagonal (i + 1, k) with k reflex
                    for j in self._reflex_vertices(i + 2, k):
                        self._tail_scan(i, j, k)  # diagonal (i, j) with i not reflex and j reflex, diagonal/edge (j, k) with j reflex and k reflex

        # recover diagonals, ordered by increasing j and then decreasing i
        self._diags = []
        self._recover_diags(0, n - 1, True)

    def _reflex_vertices(self, start, stop):
        if self._is_reflex[start]:
            i = start
        else:
            i = self._next_reflex[start]
        while i < stop:
            yield i
            i = self._next_reflex[i]

    def _is_visible(self, i, k):
        return self._rx_weight[i][self._rx[k]] is not None

    def _get_weight(self, i, k):
        return self._rx_weight[i][self._rx[k]]

    def _set_weight(self, i, k, w):
        self._rx_weight[i][self._rx[k]] = w

    def _new_deque(self, i, k):
        self._rx_deque[i][self._rx[k]] = PairDeque()

    def _get_deque(self, i, k):
        return self._rx_deque[i][self._rx[k]]

    def _update(self, i, k, w, a, b):
        ow = self._get_weight(i, k)
        if w <= ow:
            deque = self._get_deque(i, k)
            if w < ow:
                self._set_weight(i, k, w)
                deque.clear()
            deque.push(a, b)

    def _head_scan(self, i, j, k):
        if i < j - 1 and not self._is_visible(i, j) or j < k - 1 and not self._is_visible(j, k):
            return
        a = j
        w = 0
        if i < j - 1:
            w += self._get_weight(i, j)
            dq = self._get_deque(i, j)
            if not clockwise(self._P[dq.head_b()], self._P[j], self._P[k]):
                while dq.head_size() > 1 and not clockwise(self._P[dq.head_next_b()], self._P[j], self._P[k]):
                    dq.head_pop()
                if dq.head_size() > 0 and not clockwise(self._P[k], self._P[i], self._P[dq.head_a()]):
                    a = dq.head_a()
                else:
                    w += 1  # diagonal (i, j) is used
            else:
                w += 1  # diagonal (i, j) is used
        if j < k - 1:
            w += self._get_weight(j, k)
            w += 1  # diagonal (j, k) is used
        self._update(i, k, w, a, j)

    def _tail_scan(self, i, j, k):
        if i < j - 1 and not self._is_visible(i, j) or j < k - 1 and not self._is_visible(j, k):
            return
        b = j
        w = 0
        if i < j - 1:
            w += self._get_weight(i, j)
            w += 1  # diagonal (i, j) is used
        if j < k - 1:
            w += self._get_weight(j, k)
            dq = self._get_deque(j, k)
            if not clockwise(self._P[i], self._P[j], self._P[dq.tail_a()]):
                while dq.tail_size() > 1 and not clockwise(self._P[i], self._P[j], self._P[dq.tail_prev_a()]):
                    dq.tail_pop()
                if dq.tail_size() > 0 and not clockwise(self._P[dq.tail_b()], self._P[k], self._P[i]):
                    b = dq.tail_b()
                else:
                    w += 1  # diagonal (j, k) is used
            else:
                w += 1  # diagonal (j, k) is used
        self._update(i, k, w, j, b)

    def _recover_diags(self, i, k, ik_used):
        deque = self._get_deque(i, k)
        if self._is_reflex[i]:
            a = deque.head_a()
            j = deque.head_b()
            if i < j - 1:
                ij_used = a == j
                if not ij_used:
                    dq = self._get_deque(i, j)
                    dq.head_reset()
                    while dq.head_size() > 0 and dq.head_a() != a:
                        dq.head_pop()
                self._recover_diags(i, j, ij_used)
            if j < k - 1:
                self._recover_diags(j, k, True)
        else:
            j = deque.tail_a()
            b = deque.tail_b()
            if i < j - 1:
                self._recover_diags(i, j, True)
            if j < k - 1:
                jk_used = j == b
                if not jk_used:
                    dq = self._get_deque(j, k)
                    dq.tail_reset()
                    while dq.tail_size() > 0 and dq.tail_b() != b:
                        dq.tail_pop()
                self._recover_diags(j, k, jk_used)
        if ik_used:
            self._diags.append((i, k))

    def diags(self):
        return self._diags[:-1]

    def parts(self):
        parts = [None] * len(self._diags)
        p = 0
        stack = [0]
        for j in range(1, len(self._P)):
            while p < len(self._diags) and self._diags[p][1] == j:
                i = self._diags[p][0]
                parts[p] = [self._P[j]]
                while stack[-1] != i:
                    parts[p].append(self._P[stack.pop()])
                parts[p].append(self._P[i])
                parts[p].reverse()
                p += 1
            stack.append(j)
        return parts
