#so i herd u liek cedar
from cedar.cedar import Cedar

help_text = """\
DESCRIPTION
  cedar will generate a cartograph of a minecraft seed

USAGE

  python cedar.py [options ...]

OPTIONS
  --center      Point to center cartrograph on, e.g. "-50,100". If not set, map is
                centered on default spawnpoint.

  --jar         Path to jar file to use. If not set, the latest vanilla server jar
                is downloaded.

  --output      Path to where cartograph should be saved. Defaults to "{seed}.png".

  --radius      Rectangular distance from center to edge of area to be cartographed.
                Defaults to "400".

  --resolution  How many blocks to move for each pixel in the cartograph. Should be
                one of {1, 2, 4, 8, 16}. Defaults to "1".

  --seed        Seed to generate. If not set, use a random seed.

  --verbosity   Amount of log output shown. Should be one of {0, 1, 2}. Defaults to "1".
"""


class CedarStartupException(Exception):
    pass

def main(args):
    config = {
        'center': None,
        'jar': None,
        'output': 'seed_{seed}.png',
        'radius': 400,
        'resolution': 1,
        'seed': None,
        'verbosity': 1
    }

    while len(args) > 0:
        a_name = args.pop(0)
        if a_name in ('-h', '--help'):
            print(help_text)
            return
        elif a_name.startswith('--'):
            if a_name[2:] in config:
                if len(args) > 0:
                    a_value = args.pop(0)
                    config[a_name[2:]] = a_value
                else:
                    raise CedarStartupException("option missing value: {0}".format(a_name))
            else:
                raise CedarStartupException("unknown option: {0}".format(a_name))
        else:
            raise CedarStartupException("unexpected input: {0}".format(a_name))

    for k in ('radius', 'resolution', 'verbosity'):
        config[k] = int(config[k])

    c = config.get('center')
    if c:
        c = tuple(int(c) for c in c.split(',', 1))
        if len(c) != 2:
            raise CedarStartupException("invalid centerpoint")
        config['center'] = c

    config['radius'] = (config['radius']//16)*16

    Cedar(**config)


if __name__ == '__main__':
    import sys
    try:
        main(sys.argv[1:])
    except CedarStartupException as e:
        print("cedar: {0}".format(e))