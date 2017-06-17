import struct
import unittest
from pathlib import Path
from pyparsing import Word, Group, Suppress, Regex, Keyword, Forward, Optional, QuotedString, ZeroOrMore, \
                      ParseException, alphas, alphanums, hexnums, nums, pythonStyleComment

import common.scstypes as scstypes


class MapFile(dict):
    """ SCS annotated file (.mbd, .base, .aux, .desc) parsed as a hierarchical tree of values, lists & dictionaries """

    # region Grammar Definition and Type Constructors
    class Grammar:
        """ Lexical grammar of text (non-binary) SCS map (.mbd) file """

        class Parse:
            """ Helper class holding static methods to parse each type """
            @staticmethod
            def int(toks: list) -> list:
                """ Parse ordinary int or big endian hex string as a 8-byte unsigned integer """
                if toks[0].startswith('x'):
                    binary = bytes.fromhex(toks[0][1:] + '0')
                    toks[0] = struct.unpack('<Q', binary)[0]
                elif toks[0].startswith('i'):
                    toks[0] = int(toks[0][1:])
                else:
                    toks[0] = int(toks[0])
                return toks

            @staticmethod
            def float(toks: list) -> list:
                """ Parse fixed precision float or little endian hex string as a 4-byte float """
                if toks[0].startswith('i'):
                    toks[0] = int(toks[0][1:]) / 256
                else:
                    binary = bytes.fromhex(toks[0][1:])
                    toks[0] = struct.unpack('>f', binary)[0]
                return toks

        entry = Forward()
        identifier = Word(alphas, alphanums + '_')

        tokenValue = QuotedString('"')
        token = Keyword('token') + identifier + Suppress(':') + tokenValue

        intValue = (Word('x', hexnums) ^ Word('-' + nums)).setParseAction(Parse.int)
        int = Regex('[us][1-9]+') + identifier + Suppress(':') + intValue

        floatValue = (Word('&', hexnums) ^ Word('i', '-' + nums)).setParseAction(Parse.float)
        float = Keyword('float') + identifier + Suppress(':') + floatValue

        fixed2Values = Group(floatValue + floatValue)
        fixed2 = Keyword('fixed2') + identifier + Suppress(':') + fixed2Values

        fixed3Values = Group(floatValue + floatValue + floatValue)
        fixed3 = Keyword('fixed3') + identifier + Suppress(':') + fixed3Values

        float4Value = Group(floatValue + floatValue + floatValue + floatValue)
        float4 = Keyword('float4') + identifier + Suppress(':') + float4Value

        quaternionValues = Group(floatValue + floatValue + floatValue + floatValue)
        quaternion = Keyword('quaternion') + identifier + Suppress(':') + quaternionValues

        structMembers = Group(ZeroOrMore(entry))
        struct = Keyword('struct') + identifier + Suppress('{') + structMembers + Suppress('}')

        arrayFloatItems = Group(ZeroOrMore(floatValue))
        arrayFloat = Keyword('array_float') + identifier + Suppress('[') + arrayFloatItems + Suppress(']')

        arrayStructItem = Suppress('struct') + Suppress(identifier) + Suppress('{') + structMembers + Suppress('}')
        arrayStructItems = Group(ZeroOrMore(arrayStructItem))
        arrayStruct = Keyword('array_struct') + identifier + Suppress('[') + arrayStructItems + Suppress(']')

        header = Optional(Suppress('SCSAnnotatedFileV1'))
        entry << Group(int ^ float ^ float4 ^ fixed2 ^ fixed3 ^ quaternion ^ token ^ struct ^ arrayFloat ^ arrayStruct)

        file = header + ZeroOrMore(entry)
        file.ignore(pythonStyleComment)

        @classmethod
        def tokenize(cls, string: str) -> list:
            """ Perform lexical analysis and return the list of discovered tokens """
            return cls.file.parseString(string, parseAll=True).asList()

    class Reference(str):
        """ Placeholder class to keep a cross reference to another entry """
        pass

    Constructors = {
        'u8': scstypes.u8_t,
        'u16': scstypes.u16_t,
        's16': scstypes.s16_t,
        'u32': scstypes.u32_t,
        's32': scstypes.s32_t,
        'u64': scstypes.u64_t,
        's64': scstypes.s64_t,
        'token': Reference,
        'float': scstypes.float_t,
        'fixed2': scstypes.float2_t,
        'fixed3': scstypes.float3_t,
        'float4': scstypes.float4_t,
        'quaternion': scstypes.quaternion_t,
        'struct': scstypes.struct_t,
        'array_struct': scstypes.array_t,
        'array_float': scstypes.array_t
    }
    # endregion

    def __init__(self, path: Path=None):
        """ Read a SCS annotated file and parse it into a hierarchical tree of values, lists & dictionaries """
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
                       "File: \"{path.name}\"\n"
                       "Entry: \"{exc.line}\")")
                exc.msg = msg.format(exc=exc, path=path)
                raise exc

    def __getattr__(self, item) -> object:
        """ Provide nice interface to access the map file entries via dot-notation """
        return self[item] if item in self else None

    def parse(self, tokens: list):
        """ Parse a SCS annotated file into a hierarchical tree of values, lists & dictionaries """

        def structuralize(tokens: list) -> dict:
            structure = {}
            for entry in tokens:
                type, identifier, value = entry
                constructor = self.Constructors[type]
                if type == 'array_struct':
                    members = [scstypes.struct_t(structuralize(val)) for val in value]
                    value = constructor(members)
                elif type == 'struct':
                    members = structuralize(value)
                    value = constructor(members)
                else:
                    value = constructor(value)
                structure[identifier] = value
            return structure

        self.update(structuralize(tokens))


# region Unit Tests


class TestMapFile(unittest.TestCase):

    types = """
        SCSAnnotatedFileV1
        u8 type_info: 17
        u16 right_terrain_size: 500
        s32 right_road_height: -33
        u64 node0_uid: x7EC4DD7E7A00000
        token road_look: "look24"
        float right_profile_coef: &3f800000 # 1
        fixed3 position: i99088 i-2 i93331 # x:387.063 y:-0.0078125 z:364.574
        quaternion rotation: &bf78fd43 &b8d810bb &3e6e00b0 &b7ce87fd # w:-0.972614 x:-0.000103028 y:0.232424 z:-2.46204e-05
        """

    def testTypes(self):
        tokens = MapFile.Grammar.tokenize(self.types)
        correctTokens = [
            ['u8', 'type_info', 17],
            ['u16', 'right_terrain_size', 500],
            ['s32', 'right_road_height', -33],
            ['u64', 'node0_uid', 526114473086],
            ['token', 'road_look', 'look24'],
            ['float', 'right_profile_coef', 1.0],
            ['fixed3', 'position', [387.0625, -0.0078125, 364.57421875]],
            ['quaternion', 'rotation', [-0.9726144671440125, -0.00010302798909833655,
                                        0.23242449760437012, -2.462043812556658e-05]]
        ]
        self.assertListEqual(tokens, correctTokens)
        tree = MapFile()
        tree.parse(tokens)
        correctTree = {
            'type_info': scstypes.u8_t(17),
            'right_terrain_size': scstypes.u16_t(500),
            'right_road_height': scstypes.s32_t(-33),
            'node0_uid': scstypes.u64_t(526114473086),
            'road_look': MapFile.Reference('look24'),
            'right_profile_coef': scstypes.float_t(1.0),
            'position': scstypes.float3_t([387.0625, -0.0078125,  364.57421875]),
            'rotation': scstypes.quaternion_t([-0.9726144671440125, -0.00010302798909833655,
                                               0.23242449760437012, -2.462043812556658e-05])
        }
        self.assertDictEqual(tree, correctTree)

    struct = """
        struct node_item {
            u64 uid: x7EC4DD453100000
            fixed3 position: i99088 i-2 i93331 # x:387.063 y:-0.0078125 z:364.574
            quaternion rotation: &bf78fd43 &b8d810bb &3e6e00b0 &b7ce87fd # w:-0.972614 x:-0.000103028 y:0.232424 z:-2.46204e-05
            u64 backward_item_uid: x7EC4DD417500001
            u64 forward_item_uid: x7EC4DD707E00001
            u32 flags: 1
        }
        """

    def testStruct(self):
        tokens = MapFile.Grammar.tokenize(self.struct)
        correctTokens = [
            ['struct', 'node_item', [
                ['u64', 'uid', 211625559166],
                ['fixed3', 'position', [387.0625, -0.0078125, 364.57421875]],
                ['quaternion', 'rotation',
                    [-0.9726144671440125, -0.00010302798909833655,
                     0.23242449760437012, -2.462043812556658e-05]],
                ['u64', 'backward_item_uid', 1152922008223073406],
                ['u64', 'forward_item_uid', 1152922047666308222],
                ['u32', 'flags', 1]]
            ]
        ]
        self.assertListEqual(tokens, correctTokens)
        tree = MapFile()
        tree.parse(tokens)
        correctTree = {
            'node_item': scstypes.struct_t({
                'uid': scstypes.u64_t(211625559166),
                'position': scstypes.float3_t([387.0625, -0.0078125, 364.57421875]),
                'rotation': scstypes.quaternion_t([-0.9726144671440125, -0.00010302798909833655,
                                                   0.23242449760437012, -2.462043812556658e-05]),
                'forward_item_uid': scstypes.u64_t(1152922047666308222),
                'backward_item_uid': scstypes.u64_t(1152922008223073406),
                'flags': scstypes.u32_t(1)
            })
        }
        self.assertDictEqual(tree, correctTree)

    arrayFloat = """
        array_float minimums [
            &43a95780 # 338.684
            &c1780000 # -15.5
            &4348ae00 # 200.68
            &43941300 # 296.148
            &41e07800 # 28.0586
        ]
       """

    def testArrayFloat(self):
        tokens = MapFile.Grammar.tokenize(self.arrayFloat)
        correctTokens = [
            ['array_float', 'minimums', [338.68359375, -15.5, 200.6796875, 296.1484375, 28.05859375]]
        ]
        self.assertListEqual(tokens, correctTokens)
        tree = MapFile()
        tree.parse(tokens)
        correctTree = {
            'minimums': scstypes.array_t([338.68359375, -15.5, 200.6796875, 296.1484375, 28.05859375])
        }
        self.assertDictEqual(tree, correctTree)

    arrayStruct = """
        array_struct right_vegetation [
            struct vegetation {
                token vegetation: "grass"
                u16 density: 4000
                u8 hi_poly_distance: 50
                u8 scale_type: 0
                u16 start: 0
                u16 end: 0
            }
            struct vegetation {
                token vegetation: "corn"
                u16 density: 8000
                u8 hi_poly_distance: 500
                u8 scale_type: 0
                u16 start: 1
                u16 end: 1
            }
        ]
        """

    def testArrayStruct(self):
        tokens = MapFile.Grammar.tokenize(self.arrayStruct)
        correctTokens = [
            ['array_struct', 'right_vegetation', [
                [
                    ['token', 'vegetation', 'grass'],
                    ['u16', 'density', 4000],
                    ['u8', 'hi_poly_distance', 50],
                    ['u8', 'scale_type', 0],
                    ['u16', 'start', 0],
                    ['u16', 'end', 0]
                ],
                [
                    ['token', 'vegetation', 'corn'],
                    ['u16', 'density', 8000],
                    ['u8', 'hi_poly_distance', 500],
                    ['u8', 'scale_type', 0],
                    ['u16', 'start', 1],
                    ['u16', 'end', 1]
                ]]
            ]
        ]
        self.assertListEqual(tokens, correctTokens)
        tree = MapFile()
        tree.parse(tokens)
        correctTree = {
            'right_vegetation': [
                scstypes.struct_t({
                    'vegetation': scstypes.string_t('grass'),
                    'density': scstypes.u16_t(4000),
                    'hi_poly_distance': scstypes.u64_t(50),
                    'scale_type': scstypes.u8_t(0),
                    'start': scstypes.u16_t(0),
                    'end': scstypes.u16_t(0)
                }),
                scstypes.struct_t({
                    'vegetation': scstypes.string_t('corn'),
                    'density': scstypes.u16_t(8000),
                    'hi_poly_distance': scstypes.u64_t(500),
                    'scale_type': scstypes.u8_t(0),
                    'start': scstypes.u16_t(1),
                    'end': scstypes.u16_t(1)
                })
            ]
        }
        self.assertDictEqual(tree, correctTree)


# endregion
