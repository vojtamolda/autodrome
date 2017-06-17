import struct
import unittest
import warnings
from pathlib import Path
from pyparsing import Word, Group, Suppress, Combine, Optional, QuotedString, Keyword, ZeroOrMore, CharsNotIn, \
                      ParseException, alphanums, nums, hexnums, delimitedList, \
                      cStyleComment, dblSlashComment, pythonStyleComment

import common.scstypes as scstypes


class DefinitionFile(dict):
    """ SCS definition (.sii) file parsed as a hierarchical tree of values, lists & dictionaries """

    # region Grammar Definition and Type Constructors
    class Grammar:
        """ Lexical grammar of SCS definition (.sii) file """

        class Parse:
            """ Helper class holding static methods that prepend type information """
            @staticmethod
            def int(toks):
                """ Parse an ordinary int value """
                toks[0] = int(toks[0])
                return toks

            @staticmethod
            def float(toks):
                """ Parse an ordinary float or little endian hex string as a 4-byte float """
                if toks[0].startswith('&'):
                    binary = bytes.fromhex(toks[0][1:])
                    toks[0] = struct.unpack('>f', binary)[0]
                else:
                    toks[0] = float(toks[0])
                return toks

            @staticmethod
            def bool(toks):
                """ Parse bool True or False value """
                toks[0] = (toks[0] == 'true')
                return toks

            @staticmethod
            def reference(toks):
                """ Parse delayed cross reference to an entry """
                toks[0] = DefinitionFile.Reference(toks[0])
                return toks

            @staticmethod
            def tuple(toks):
                """ Parse a tuple into the corresponding floatN_t"""
                if len(toks[0]) == 2:
                    toks[0] = scstypes.float2_t(toks[0])
                elif len(toks[0]) == 3:
                    toks[0] = scstypes.float3_t(toks[0])
                elif len(toks[0]) == 4:
                    toks[0] = scstypes.float4_t(toks[0])
                else:
                    toks[0] = tuple(toks[0])
                return toks

            @staticmethod
            def include(toks):
                """ Include content of another definition file """
                raise NotImplementedError

        identifier = Word(alphanums + '_')
        name = Optional(Suppress('"')) + Word(alphanums + '.' + '_') + Optional(Suppress('"'))

        intValue = Word(nums + '-', nums).setParseAction(Parse.int)
        int = identifier + Suppress(':') + intValue
        int.setParseAction(lambda toks: toks.insert(0, 'int'))

        binaryFloat = Word('&', hexnums)
        regularFloat = Word(nums + '-', nums + '.' + 'eE' + '-')
        floatValue = (regularFloat ^ binaryFloat).setParseAction(Parse.float)
        float = identifier + Suppress(':') + floatValue
        float.setParseAction(lambda toks: toks.insert(0, 'float'))

        boolValue = (Keyword('true') ^ Keyword('false')).setParseAction(Parse.bool)
        bool = identifier + Suppress(':') + boolValue
        bool.setParseAction(lambda toks: toks.insert(0, 'bool'))

        textValue = QuotedString('"') ^ identifier
        text = identifier + Suppress(':') + textValue
        text.setParseAction(lambda toks: toks.insert(0, 'text'))

        tupleValue = Group(Suppress('(') + delimitedList(intValue ^ floatValue, delim=',') + Suppress(')'))
        tupleValue.setParseAction(Parse.tuple)
        tuple = identifier + Suppress(':') + tupleValue
        tuple.setParseAction(lambda toks: toks.insert(0, 'tuple'))

        referenceValue = Word(alphanums + '.' + '_').setParseAction(Parse.reference)
        reference = identifier + Suppress(':') + referenceValue
        reference.setParseAction(lambda toks: toks.insert(0, 'reference'))

        arrayValue = (intValue ^ floatValue ^ boolValue ^ textValue ^ tupleValue ^ referenceValue)
        array = Combine(identifier + Suppress('[' + Optional(intValue) + ']')) + Suppress(':') + arrayValue
        array.setParseAction(lambda toks: toks.insert(0, 'array'))

        label = Group(identifier + Suppress(':') + name)
        property = Group(int ^ float ^ bool ^ text ^ tuple ^ reference ^ array)
        include = Suppress(Keyword('@include')) + QuotedString('"').setParseAction(Parse.include)
        entry = label + Suppress('{') + ZeroOrMore(property ^ include) + Suppress('}')

        junk = ZeroOrMore(CharsNotIn(alphanums))
        header = Suppress(junk + Optional(Keyword('SiiNunit') + '{'))
        footer = Suppress(Optional('}'))

        file = header + ZeroOrMore(Group(entry ^ include)) + footer
        file.ignore(cStyleComment)
        file.ignore(dblSlashComment)
        file.ignore(pythonStyleComment)

        @classmethod
        def tokenize(cls, string: str) -> list:
            """ Perform lexical analysis and return the list of discovered tokens """
            return cls.file.parseString(string, parseAll=True).asList()

    class Reference(str):
        """ Placeholder class to keep a cross reference to another entry """
        pass

    Constructors = {
        'int': scstypes.s64_t,
        'bool': lambda bln: bln,
        'float': scstypes.float_t,
        'text': scstypes.string_t,
        'tuple': lambda tpl: tpl,
        'reference': Reference,
        'array': scstypes.array_t,
    }
    # endregion

    def __init__(self, path: Path=None):
        """ Read a SCS definition (.sii) file and parse it into a hierarchical tree of values, lists & dictionaries """
        super().__init__()
        self.path = path
        if path is None:
            return
        with path.open('rt') as file:
            try:
                content = file.read()
                tokens = self.Grammar.tokenize(content)
                self.parse(tokens)
            except ParseException as exc:
                msg = ("{exc.msg}\n"
                       "File \"{path}\"\n"
                       "Entry \"{exc.line}\")")
                exc.msg = msg.format(exc=exc, path=path)
                raise exc

    def __getattr__(self, item: object) -> object:
        """ Provide nice interface to access the definition file entries via dot-notation """
        return self[item] if item in self else None

    def parse(self, tokens: list):
        """ Parse a SCS map (.mbd) file into a hierarchical tree of values, lists & dictionaries """

        def structuralize(iterator: iter) -> dict:
            structure = {}
            for kind, identifier, value in iterator:
                constructor = self.Constructors[kind]
                if kind == 'array':
                    if identifier not in structure or not isinstance(structure[identifier], constructor):
                        structure[identifier] = constructor()
                    structure[identifier].append(value)
                else:
                    if identifier in structure:
                        message = ("Duplicate value found parsing:\n"
                                   "File \"{path}\"\n"
                                   "Value \"{group}:{name}::{ident}\"")
                        message = message.format(group=group, name=name, ident=identifier, path=self.path)
                        warnings.warn(message, SyntaxWarning)
                    structure[identifier] = constructor(value)
            return structure

        for entry in tokens:
            iterator, container = iter(entry), self
            try:
                group, name = next(iterator)
            except Exception:
                continue
            for piece in name.split('.'):
                if piece not in container:
                    container[piece] = {}
                supercontainer = container
                container = container[piece]
            supercontainer[piece] = structuralize(iterator)


class Definition(dict):
    """ SCS definition data (*.sii) represented as a cross-referenced graph of dictionaries, lists and items """

    def __init__(self, directory: Path, recursive=False):
        """ Read a SCS definition files (*.sii) from a directory and merge them into a single in-memory graph """
        super().__init__()
        siiFiles = directory.glob('**/*.sii' if recursive is True else '*.sii')

        for siiFile in siiFiles:
            defs = DefinitionFile(siiFile)
            self.merge(defs)
        self.resolve()

    def merge(self, another: DefinitionFile):
        """ Recursively merge with another definition file and check for duplicate values """
        recurse = []

        def merge(this: dict, other: dict):
            for identifier, value in other.items():
                if identifier in this:
                    if isinstance(value, dict) and not isinstance(value, scstypes.struct_t):
                        recurse.append(identifier)
                        merge(this[identifier], other[identifier])
                        recurse.pop()
                    elif isinstance(value, list) and not isinstance(value, scstypes.array_t):
                        this[identifier].extend(other[identifier])
                    else:
                        message = ("Duplicate found during merging:\n"
                                   "File \"{path}\"\n"
                                   "Key \"{name}::{ident}\"")
                        message = message.format(name=".".join(recurse), ident=identifier, path=another.path)
                        warnings.warn(message, RuntimeWarning)
                        this[identifier] = value
                else:
                    this[identifier] = value

        merge(self, another)

    def resolve(self):
        """ Recursively walk the value tree, resolve references and effectively form a graph out of the tree """
        recurse = []
        iterators = {
            dict: lambda dct: dct.items(),
            list: lambda lst: enumerate(lst),
            Definition: lambda dfn: dfn.items(),
            scstypes.array_t: lambda arr: enumerate(arr),
            scstypes.struct_t: lambda dct: dct.items()
        }

        def resolve(container: object):
            for key, item in iterators[type(container)](container):
                if isinstance(item, DefinitionFile.Reference):
                    try:
                        resolved = self
                        for piece in item.split('.'):
                            resolved = resolved[piece]
                        container[key] = resolved
                    except KeyError:
                        message = ("Unresolved reference\n"
                                   "Key \"{name}::{ident}\"\n"
                                   "Reference \"{reference}\"")
                        message = message.format(name=".".join(recurse), ident=key, reference=item)
                        warnings.warn(message, RuntimeWarning)
                elif type(item) in iterators:
                    recurse.append(key)
                    resolve(item)
                    recurse.pop()

        resolve(self)

    def __sizeof__(self):
        """ Recursively calculate size of the contained data """
        from sys import getsizeof
        from inspect import getmro
        from itertools import chain

        counted = set()
        containers = {
            list: lambda lst: lst,
            tuple: lambda tpl: tpl,
            dict: lambda dct: chain(dct.keys(), dct.values())
        }

        def sizeof(item: object) -> int:
            if id(item) in counted:
                return 0
            counted.add(id(item))
            size = getsizeof(item, getsizeof(1))
            baseclass = getmro(type(item))[-2]
            if baseclass in containers:
                iterator = containers[baseclass]
                size += sum(map(sizeof, iterator(item)))
            return size

        return sum(map(sizeof, containers[dict](self)))


# region Unit Tests


class TestDefinitionFile(unittest.TestCase):

    entries = """
        SiiNunit {
        road_look : road.look3 {
            name: "Road 3"
            road_size: 3.5e-1
            target_white: &3f000000
            bloom_minimal_color: (&3f800000, &3f800000, &3f800000)
            slow_time: true
            lane_offsets_right[]: (1.25, 0)
            lane_offsets_right[]: (1.25, 3.75)
        }
        road_look : road.look5 {
            name: "Road 5"
            reference: traffic_lane.road.divided
            road_size: 5.5
            slow_time: false
            center_line_style: 2
            lanes[]: traffic_lane.road.local
            lanes[]: traffic_lane.road.highway
        }
        }
        """

    def testEntries(self):
        tokens = DefinitionFile.Grammar.tokenize(self.entries)
        correctTokens = [
            [
                ['road_look', 'road.look3'],
                ['text', 'name', 'Road 3'],
                ['float', 'road_size', 0.35],
                ['float', 'target_white', 0.5],
                ['tuple', 'bloom_minimal_color', scstypes.float3_t((1.0, 1.0, 1.0))],
                ['bool', 'slow_time', True],
                ['array', 'lane_offsets_right', scstypes.float2_t((1.25, 0))],
                ['array', 'lane_offsets_right', scstypes.float2_t((1.25, 3.75))]
            ], [
                ['road_look', 'road.look5'],
                ['text', 'name', 'Road 5'],
                ['reference', 'reference', DefinitionFile.Reference('traffic_lane.road.divided')],
                ['float', 'road_size', 5.5],
                ['bool', 'slow_time', False],
                ['int', 'center_line_style', 2],
                ['array', 'lanes', DefinitionFile.Reference('traffic_lane.road.local')],
                ['array', 'lanes', DefinitionFile.Reference('traffic_lane.road.highway')]
            ]
        ]
        self.assertListEqual(tokens, correctTokens)
        tree = DefinitionFile()
        tree.parse(tokens)
        correctTree = {
            'road': {
                'look3': {
                    'name': scstypes.string_t('Road 3'),
                    'road_size': scstypes.float_t(0.35),
                    'target_white': scstypes.float_t(0.5),
                    'bloom_minimal_color': scstypes.float3_t((1.0, 1.0, 1.0)),
                    'slow_time': True,
                    'lane_offsets_right': scstypes.array_t([scstypes.float2_t((1.25, 0)),
                                                            scstypes.float2_t((1.25, 3.75))])
                },
                'look5': {
                    'name': scstypes.string_t('Road 5'),
                    'reference': DefinitionFile.Reference('traffic_lane.road.divided'),
                    'road_size': scstypes.float_t(5.5),
                    'slow_time': False,
                    'center_line_style': scstypes.s64_t(2),
                    'lanes': scstypes.array_t([DefinitionFile.Reference('traffic_lane.road.local'),
                                               DefinitionFile.Reference('traffic_lane.road.highway')])
                }
            }
        }
        self.assertDictEqual(tree, correctTree)


class TestDefinition(unittest.TestCase):

    @unittest.skip("Definitions (def.scs) file has to be extracted manually to this location")
    def testLoad(self):
        dir = Path('/Users/Vojta/Source/scs_extracted/def/world/')
        defs = Definition(dir, recursive=True)
        pass


# endregion
