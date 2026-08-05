def vector(p, q):
    return q[0] - p[0], q[1] - p[1]


def cross(p, q):
    return p[0] * q[1] - p[1] * q[0]


def orient(p, q, r):
    return cross(vector(p, q), vector(p, r))


def clockwise(p, q, r):
    return orient(p, q, r) < 0


def line(p, q):
    return p[1] - q[1], q[0] - p[0], cross(p, q)


def det(a, b, c):
    return cross(a, b) * c[2] + cross(b, c) * a[2] + cross(c, a) * b[2]


def intersect(a, b):
    c = cross(a, b)
    x = (a[1] * b[2] - a[2] * b[1]) / c
    y = (a[2] * b[0] - a[0] * b[2]) / c
    return x, y


class Type:
    VISIBLE = 0
    LID_RIGHT = 1
    LID_LEFT = 2


class Node:
    def __init__(self, index, type):
        self.index = index
        self.type = type


class Visibility:
    def __init__(self, P, o):
        self._P = P
        self._o = o

        # initialize lid
        self._lid_left = None
        self._lid_right = None

        # initialize stack
        self._stack = [Node(0, Type.VISIBLE)]
        i = 1
        while i < len(P):
            # [NOTE] the current point is visible
            self._stack.append(Node(i, Type.VISIBLE))
            i += 1

            if i == len(P):
                break

            # [NOTE] process the next point p(i)

            if not clockwise(self._p(0), self._p(i - 1), self._p(i)):
                # [NOTE] point p(i) is visible
                continue

            if clockwise(self._p(i - 2), self._p(i - 1), self._p(i)):
                # [NOTE] point p(i) is in a right bay
                i = self._exit_right_bay(i, self._p(i - 1), (0, 0, 1))
                # [NOTE] edge (p(i - 1), p(i)) is a right lid
                self._stack.append(Node(i - 1, Type.LID_RIGHT))
                continue

            # [NOTE] edge (p(i - 1), p(i)) blocks the currently visible part

            # [NOTE] stash the current lid
            self._stash_lid()
            while True:
                if clockwise(self._p(0), self._p(self._stack[-1].index), self._p(i)):
                    # [NOTE] the current lid is completely invisible
                    self._discard_lid()
                    if clockwise(self._p(i - 1), self._p(i), self._p(self._stack[-1].index)):
                        # [NOTE] point p(i) is in a right bay, exit the right bay
                        i = self._exit_right_bay(i, self._p(self._stack[-1].index), line(self._p(i), self._p(i - 1)))
                        # [NOTE] edge (p(i - 1), p(i)) is a right lid
                        self._stack.append(Node(i - 1, Type.LID_RIGHT))
                        break
                    else:
                        # [NOTE] stash a new lid
                        self._stash_lid()
                else:
                    # [NOTE] the current lid is partially visible
                    if clockwise(self._p(0), self._p(i), self._p(i + 1)):
                        # [NOTE] point p(i) is invisible
                        i += 1
                    elif clockwise(self._p(i - 1), self._p(i), self._p(i + 1)):
                        # [NOTE] restore the current lid because it is partially visible
                        self._restore_lid()
                        # [NOTE] point p(i) is visible
                        self._stack.append(Node(i, Type.VISIBLE))
                        i += 1
                        break
                    else:
                        # [NOTE] point p(i) is in a left bay, exit the left bay
                        i = self._exit_left_bay(i, self._p(i), line(self._p(self._lid_left), self._p(self._lid_left - 1)))

    def _p(self, i):
        return self._P[(self._o + i) % len(self._P)]

    def _stash_lid(self):
        if self._stack[-2].type == Type.LID_LEFT:
            self._stack.pop()
        self._lid_left = self._stack.pop().index
        if self._stack[-1].type == Type.LID_RIGHT:
            self._lid_right = self._stack.pop().index
        else:
            self._lid_right = None

    def _restore_lid(self):
        if self._lid_right is not None:
            self._stack.append(Node(self._lid_right, Type.LID_RIGHT))
        self._stack.append(Node(self._lid_left, Type.LID_LEFT))
        self._lid_left = None
        self._lid_right = None

    def _discard_lid(self):
        self._lid_left = None
        self._lid_right = None

    def _exit_right_bay(self, i, corner, bound):
        wn = 0
        curr_right = True
        while True:
            i += 1
            prev_right = curr_right
            curr_right = clockwise(self._p(0), corner, self._p(i))
            if curr_right != prev_right and clockwise(self._p(i - 1), self._p(i), self._p(0)) == curr_right:
                if curr_right:
                    wn -= 1
                else:
                    wn += 1
                    if wn == 1 and clockwise(self._p(i), self._p(i - 1), corner) and det(line(self._p(0), corner), line(self._p(i - 1), self._p(i)), bound) > 0:
                        return i

    def _exit_left_bay(self, i, corner, bound):
        wn = 0
        curr_right = False
        while True:
            i += 1
            prev_right = curr_right
            curr_right = clockwise(self._p(0), corner, self._p(i))
            if curr_right != prev_right and clockwise(self._p(i - 1), self._p(i), self._p(0)) == curr_right:
                if curr_right:
                    wn += 1
                    if wn == 1 and clockwise(self._p(i - 1), self._p(i), corner) and det(line(self._p(0), corner), line(self._p(i - 1), self._p(i)), bound) > 0:
                        return i
                else:
                    wn -= 1

    def visible_vertices(self):
        return [(self._o + node.index) % len(self._P) for node in self._stack if node.type == Type.VISIBLE]

    def visibility_polygon(self):
        polygon = []
        for rank, node in enumerate(self._stack):
            if node.type == Type.VISIBLE:
                polygon.append(self._p(node.index))
            elif node.type == Type.LID_RIGHT:
                polygon.append(intersect(line(self._p(0), self._p(self._stack[rank - 1].index)), line(self._p(node.index), self._p(node.index + 1))))
            elif node.type == Type.LID_LEFT:
                polygon.append(intersect(line(self._p(0), self._p(self._stack[rank + 1].index)), line(self._p(node.index - 1), self._p(node.index))))
        return polygon
