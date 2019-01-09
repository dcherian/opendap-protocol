import opendap_protocol as dap

import xdrlib
import numpy as np

XDRPACKER = xdrlib.Packer()

def test_dods_encode():

    testdata = np.array(range(100), dtype=np.float32)

    xdrpacked = pack_xdr_float(testdata)

    assert xdrpacked == dap.dods_encode(testdata, dap.Float32)

    assert b'\x00\x00\x00\x00' == dap.dods_encode(0, dap.Float32)


def test_parse_slice():

    assert dap.parse_slice(':') == ...
    assert dap.parse_slice('3:7') == slice(3, 8)
    assert dap.parse_slice('4') == 4


def test_parse_slice_constraint():

    assert dap.parse_slice_constraint('[0][:][:][4:7]') == (0, ..., ..., slice(4, 8))
    assert dap.parse_slice_constraint('[0][:][:]') == (0, ..., ...)
    assert dap.parse_slice_constraint('[0][:]') == (0, ...)
    assert dap.parse_slice_constraint('[0]') == (0, )
    assert dap.parse_slice_constraint('[]') == (..., )


def test_meets_constraint():

    assert dap.meets_constraint('', 'test.object.path')

    assert dap.meets_constraint('test.object.path', 'test')
    assert dap.meets_constraint('test.object.path', 'test.object')
    assert dap.meets_constraint('test.object.path', 'test1.object') is False


def test_DAPObject():

    ob1 = dap.DAPObject(name='Object 1')
    assert ob1.name == 'Object_1'

    ob2 = dap.DAPObject(name='Object_2', parent=ob1)
    assert ob2.name == 'Object_2'
    assert ob2.parent.name == 'Object_1'

    ob3 = dap.DAPObject(name=1)
    assert ob3.name == 1


def test_Dataset():

    dataset = dap.Dataset(name='data')
    assert dataset.name == 'data'
    assert dataset.parent is None
    assert dataset.indent == ''
    assert dataset.data_path == ''

    assert b'Data:' in b''.join(dataset.dods_data())

    ob1 = dap.DAPObject(name='Object 1')

    dataset.append(ob1)

    assert ob1.data_path == 'Object_1'
    assert ob1.indent == '    '


def test_Attribute():

    dataset = dap.Dataset(name='test')

    attr1 = dap.Attribute(name='Attribute 1', value=3, dtype=dap.Float32)
    attr2 = dap.Attribute(name='Attribute 2', value='a string', dtype=dap.String)

    dataset.append(attr1, attr2)

    assert attr1.indent == '    '
    assert attr2.indent == '    '

    assert 'Float32' in ''.join(attr1.das())
    assert '"' in ''.join(attr2.das())

    assert 'Attribute' not in ''.join(dataset.dds())


def test_DAPAtom():

    pass

def pack_xdr_float(data):
    XDRPACKER.reset()
    XDRPACKER.pack_int(np.asarray(len(data)).astype('<i4'))
    XDRPACKER.pack_int(np.asarray(len(data)).astype('<i4'))
    XDRPACKER.pack_farray(len(data), data, XDRPACKER.pack_float)
    return XDRPACKER.get_buffer()

