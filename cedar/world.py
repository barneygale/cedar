import gzip
import struct
import zlib

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from lib.nbt import NBTFile

class World:
    leveldat = 'world/level.dat'
    region   = 'world/region/r.{0}.{1}.mca'

    def __init__(self, log):
        self.log = log
        with gzip.open(self.leveldat, 'rb') as io:
            data = NBTFile(io)['Data']

            self.spawn = (data['SpawnX'].value, data['SpawnZ'].value)
            self.seed = data['RandomSeed'].value

    def set_spawn(self, spawn):
        with gzip.open(self.leveldat, 'rb') as io:
            nbt = NBTFile(io)

        nbt['Data']['SpawnX'].value = spawn[0]
        nbt['Data']['SpawnZ'].value = spawn[1]

        with gzip.open(self.leveldat, 'wb') as io:
            nbt.save(io)

    def carto(self, radius, center=(0,0), resolution=1):
        c_lower = tuple((c-radius)//16     for c in center)
        c_upper = tuple((c+radius)//16 - 1 for c in center)

        r_count = (1 + c_upper[0]//32 - c_lower[0]//32) * (1 + c_upper[1]//32 - c_lower[1]//32)
        r_index = 1

        #Loop over regions
        for rz in range(c_lower[1]//32, 1 + c_upper[1]//32):
            for rx in range(c_lower[0]//32, 1 + c_upper[0]//32):
                self.log(1, 'generating carto ({0} of {1})'.format(r_index, r_count))
                r_index += 1

                r_file = open(self.region.format(rx, rz), 'rb')
                chunk_offsets = []

                #Read the header .mca header
                for cz in range(32):
                    for cx in range(32):
                        r_tmp = r_file.read(4)

                        #Ignore chunks we don't care about
                        if c_lower[0] <= cx + rx * 32 <= c_upper[0] and \
                           c_lower[1] <= cz + rz * 32 <= c_upper[1]:
                            r_tmp = struct.unpack('>I', r_tmp)[0]
                            chunk_offsets.append((cz, cx, r_tmp >> 8))

                #Loop over 16x16 chunks
                for cz, cx, offset in chunk_offsets:

                    #Read
                    r_file.seek(offset * 4096, 0)
                    c_size, c_compression = struct.unpack('>iB', r_file.read(5))
                    c_data = r_file.read(c_size)

                    #Decompress
                    c_data = zlib.decompress(c_data)

                    #Load
                    c_nbt = NBTFile(io=StringIO(c_data))['Level']
                    c_heightmap = c_nbt['HeightMap'].value
                    c_biomes = c_nbt['Biomes'].value
                    c_sections = {s['Y'].value: s for s in c_nbt['Sections']}

                    #Loop over 1x1 columns
                    for pz in range(0, 16, resolution):
                        for px in range(0, 16, resolution):

                            fx = rx * 512 + cx * 16 + px
                            fz = rz * 512 + cz * 16 + pz

                            f_height = c_heightmap[16 * pz + px]-1
                            f_biome  = c_biomes   [16 * pz + px]
                            p_section, p_inner = divmod(f_height, 16)

                            # key for input byte array
                            f_key1 = 256 * p_inner + 16 * pz + px
                            # key info for input nibble array
                            f_key2 = divmod(f_key1, 2)

                            f_data = c_sections[p_section]['Blocks'].value[f_key1] % 256
                            f_meta = c_sections[p_section]['Data'].value[f_key2[0]] % 256
                            f_meta = f_meta >> 4 if f_key2[1] == 0 else f_meta & 0x0F

                            yield fx, fz, f_data, f_meta, f_height, f_biome

                r_file.close()