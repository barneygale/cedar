import os

#temp directory
import tempfile
import shutil
import contextlib

#jar downloader
import urllib2
import json

#cedar code
from blocks import BlockColours
from spiral import Spiral
from world import World
from wrapper import Wrapper
from lib.png import Writer


@contextlib.contextmanager
def tempdir(*a, **k):
    tmp = tempfile.mkdtemp(*a, **k)
    try:
        yield tmp
    finally:
        shutil.rmtree(tmp)


class Cedar:
    def __init__(self, center=None, jar=None, output='{seed}.png', radius=1000, resolution=2, seed=None, verbosity=1):
        self.verbosity = verbosity

        # Resolve paths before we change directory
        output = os.path.abspath(output)
        if jar:
            jar = os.path.abspath(jar)

        #Make a temporary directory and switch to it
        self.log(1, 'creating temporary directory')
        with tempdir(prefix='cedar-tmp-') as tmp:
            os.chdir(tmp)

            #Copy in the server jar, or download it
            if jar:
                self.log(1, 'copying jar')
                source = open(jar, 'rb')
            else:
                self.log(1, 'downloading jar')
                source = self.download_server()

            dest = open('minecraft_server.jar', 'wb')
            dest.write(source.read())
            source.close()
            dest.close()

            #Auto validating EULA
            self.log(1, 'Auto validating EULA')
            with open('eula.txt', 'w') as eula:
                eula.write('eula={ebval}'.format(ebval='true'))

            #Write server.properties
            self.log(1, 'writing server.properties')
            with open('server.properties', 'w') as props:
                props.write('level-seed={seed}\nlisten-port=65349\n'.format(seed=seed if seed else ''))

            #Do a first-run of the server
            self.log(1, 'initialising world')
            wrapper = Wrapper(self.log)
            wrapper.run()

            #Grab spawn point and seed, if they haven't been specified
            world = World(self.log)
            if not center:
                center = world.spawn
            if not seed:
                seed = world.seed

            center = tuple((c//16)*16 for c in center)
            output = output.format(seed=seed)

            #Open output image
            img = open(output, 'wb')

            #Generate the world!
            path = list(Spiral.spiral(radius, center))
            for i, spawn in enumerate(path):
                self.log(1, "generating world ({0} of {1})".format(i+1, len(path)))
                world.set_spawn(spawn)
                wrapper.run()

            #Generate the carto!
            colours = BlockColours()
            size = 2 * radius // resolution
            writer = Writer(size, size)
            pixels = [0] * (size * size * 3)
            for b_x, b_z, b_data, b_meta, b_height, b_biome in world.carto(radius, center, resolution):
                try:
                    colour = colours.get_colour(b_data, b_meta)
                except KeyError:
                    self.log(1, "unknown block at {0}, {1}! id: {2} meta: {3}".format(b_x, b_z, b_data, b_meta))
                    continue
                b_x = (b_x + radius - center[0]) // resolution
                b_z = (b_z + radius - center[1]) // resolution
                for i, c in enumerate(colour):
                    pixels[i + 3 * (b_x + size*b_z)] = c

            writer.write_array(img, pixels)
            img.close()

            self.log(1, "saved as {0}".format(output))

    def download_server(self):
        base = 'http://s3.amazonaws.com/Minecraft.Download/versions/'

        #get version
        data = urllib2.urlopen(base + 'versions.json').read()
        data = json.loads(data)
        version = data['latest']['release']

        #get server
        return urllib2.urlopen(base + '{0}/minecraft_server.{0}.jar'.format(version))

    def log(self, level, msg):
        if self.verbosity >= level:
            print("... {0}".format(msg))
