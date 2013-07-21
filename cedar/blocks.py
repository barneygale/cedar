import os
import re
import zipfile

from lib.png import Reader

class BlockColours(dict):
    def __init__(self):
        super(BlockColours, self).__init__()
        self.path = os.path.join(os.path.dirname(__file__), 'data', 'blocks.txt')
        with open(self.path, 'r') as f:
            for line in f:
                if line[0] in '#\n':
                    continue
                split = re.split('\s+', line.rstrip(), 6)

                b_id     = int(split[0])
                b_meta   = split[1] if split[1] == '-' else int(split[1])
                b_colour = [int(c) for c in split[2:5]]
                b_tex    = split[5]
                b_notes  = split[6] if len(split) > 6 else ""
                self[(b_id, b_meta)] = [b_colour, b_tex, b_notes]

    def get_colour(self, i, m):
        v = self.get((i, '-'))
        if v: return v[0]

        v = self.get((i, m))
        if v: return v[0]
        raise KeyError()

    def set_colour(self, i, m, c):
        self[(i, m)][0] = c

    def load_from_jar(self, jar):
        for k, v in self.iteritems():
            if v[1] == '-':
                continue

            with jar.open('assets/minecraft/textures/blocks/{0}.png'.format(v[1])) as f:
                reader = Reader(file=f)
                width, height, pixels, metadata = reader.read_flat()

            avg_n = [0, 0, 0]
            avg_d = 0
            planes = metadata['planes']
            for i in range(width**2):
                pixel = pixels[i*planes:(i+1)*planes]
                avg_g = pixel[3] if planes == 4 else 255
                avg_n = [a+b*avg_g for a, b in zip(avg_n, pixel[:3])]
                avg_d += avg_g

            self.set_colour(k[0], k[1], [n/avg_d for n in avg_n])

    def save(self):
        line = lambda *a: "".join([str(t).ljust(8) for t in a[:5]] + [a[5].ljust(32), a[6], "\n"])

        out = line('#id', '#meta', '#red', '#green', '#blue', '#texture', '#notes')

        for key in sorted(self.keys()):
            value = self[key]
            out += line(key[0], key[1], value[0][0], value[0][1], value[0][2], value[1], value[2])

        with open(self.path, 'w') as f:
            f.write(out)

    def make_safe(self):
        return { '{0},{1}'.format(*k) : v[0] for k, v in self.iteritems() }


#TODO: move this somewhere nice
if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    if len(args) == 1:
        colours = BlockColours()
        jar = zipfile.ZipFile(args[0], 'r')
        colours.load_from_jar(jar)
        colours.save()
    else:
        print "usage: python blocks.py /path/to/minecraft.jar"