square = 16 * 25

class Spiral:
    @classmethod
    def spiral(cls, radius, start=(0,0)):
        clip1 = (2*radius - 1)//square
        clip2 = max(0, radius - square//2)
        offset1 = (clip1 % 2) * square//2

        for p in cls.spiral_inner(pow(clip1+1, 2)):
            yield tuple(
                v +                          # start co-ordinate
                max(-clip2,                  # clamp low
                    min(clip2,               # clamp high
                        offset1 +            # apply offset for even-numbered grids
                        w * square))         # operate in steps of square
                for v, w in zip(start, p))   # zip current spiral coords with start coords


    @classmethod
    def spiral_inner(cls, m):
        yield (0, 0)
        m -= 1

        d = lambda a: (0, 1, 0, -1)[a % 4]
        x = z = 0
        i = 2
        while m > 0:
            for j in range(i >> 1):
                x += d(i)
                z += d(i+1)
                yield (x, z)
                m -= 1
                if m == 0:
                    break
            i += 1