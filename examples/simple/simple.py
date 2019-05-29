import os
import pyffi.engines.xml
import pyffi.types.common


class SimpleFormat(pyffi.engines.xml.FileFormat):
    xml_file_name = 'simple.xml'
    xml_file_path = [ os.path.dirname(__file__) ]

    # basic types

    Int = pyffi.types.common.Int

    # extensions of generated types

    class Data(pyffi.engines.xml.FileFormat.Data):
        def __init__(self):
            self.example = SimpleFormat.Example()

        def read(self, stream):
            self.example.read(stream, self)

        def write(self, stream):
            self.example.write(stream, self)

    class Example:
        def addInteger(self, x):
            self.numIntegers += 1
            self.integers.update_size()
            self.integers[self.numIntegers-1] = x
