#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Hamilton Kibbe <ham@hamiltonkib.be>
from ..cam import FileSettings
from ..excellon import read, detect_excellon_format, ExcellonFile, ExcellonParser
from tests import *

import os

NCDRILL_FILE = os.path.join(os.path.dirname(__file__),
                                'resources/ncdrill.DRD')

def test_format_detection():
    """ Test file type detection
    """
    settings = detect_excellon_format(NCDRILL_FILE)
    assert_equal(settings['format'], (2, 4))
    assert_equal(settings['zeros'], 'trailing')

def test_read():
    ncdrill = read(NCDRILL_FILE)
    assert(isinstance(ncdrill, ExcellonFile))

def test_read_settings():
    ncdrill = read(NCDRILL_FILE)
    assert_equal(ncdrill.settings['format'], (2, 4))
    assert_equal(ncdrill.settings['zeros'], 'trailing')

def test_bounds():
    ncdrill = read(NCDRILL_FILE)
    xbound, ybound = ncdrill.bounds
    assert_array_almost_equal(xbound, (0.1300, 2.1430))
    assert_array_almost_equal(ybound, (0.3946, 1.7164))

def test_report():
    ncdrill = read(NCDRILL_FILE)

def test_parser_hole_count():
    settings = FileSettings(**detect_excellon_format(NCDRILL_FILE))
    p = ExcellonParser(settings)
    p.parse(NCDRILL_FILE)
    assert_equal(p.hole_count, 36)

def test_parser_hole_sizes():
    settings = FileSettings(**detect_excellon_format(NCDRILL_FILE))
    p = ExcellonParser(settings)
    p.parse(NCDRILL_FILE)
    assert_equal(p.hole_sizes, [0.0236, 0.0354, 0.04, 0.126, 0.128])

def test_parse_whitespace():
    p = ExcellonParser(FileSettings())
    assert_equal(p._parse('         '), None)

def test_parse_comment():
    p = ExcellonParser(FileSettings())
    p._parse(';A comment')
    assert_equal(p.statements[0].comment, 'A comment')

def test_parse_format_comment():
    p = ExcellonParser(FileSettings())
    p._parse('; FILE_FORMAT=9:9 ')
    assert_equal(p.format, (9, 9))

def test_parse_header():
    p = ExcellonParser(FileSettings())
    p._parse('M48   ')
    assert_equal(p.state, 'HEADER')
    p._parse('M95   ')
    assert_equal(p.state, 'DRILL')

def test_parse_rout():
    p = ExcellonParser(FileSettings())
    p._parse('G00  ')
    assert_equal(p.state, 'ROUT')
    p._parse('G05 ')
    assert_equal(p.state, 'DRILL')

def test_parse_version():
    p = ExcellonParser(FileSettings())
    p._parse('VER,1  ')
    assert_equal(p.statements[0].version, 1)
    p._parse('VER,2  ')
    assert_equal(p.statements[1].version, 2)

def test_parse_format():
    p = ExcellonParser(FileSettings())
    p._parse('FMAT,1  ')
    assert_equal(p.statements[0].format, 1)
    p._parse('FMAT,2  ')
    assert_equal(p.statements[1].format, 2)

def test_parse_units():
    settings = FileSettings(units='inch', zeros='trailing')
    p = ExcellonParser(settings)
    p._parse(';METRIC,LZ')
    assert_equal(p.units, 'inch')
    assert_equal(p.zeros, 'trailing')
    p._parse('METRIC,LZ')
    assert_equal(p.units, 'metric')
    assert_equal(p.zeros, 'leading')

def test_parse_incremental_mode():
    settings = FileSettings(units='inch', zeros='trailing')
    p = ExcellonParser(settings)
    assert_equal(p.notation, 'absolute')
    p._parse('ICI,ON  ')
    assert_equal(p.notation, 'incremental')
    p._parse('ICI,OFF  ')
    assert_equal(p.notation, 'absolute')

def test_parse_absolute_mode():
    settings = FileSettings(units='inch', zeros='trailing')
    p = ExcellonParser(settings)
    assert_equal(p.notation, 'absolute')
    p._parse('ICI,ON  ')
    assert_equal(p.notation, 'incremental')
    p._parse('G90  ')
    assert_equal(p.notation, 'absolute')

def test_parse_repeat_hole():
    p = ExcellonParser(FileSettings())
    p._parse('R03X1.5Y1.5')
    assert_equal(p.statements[0].count, 3)

def test_parse_incremental_position():
    p = ExcellonParser(FileSettings(notation='incremental'))
    p._parse('X01Y01')
    p._parse('X01Y01')
    assert_equal(p.pos, [2.,2.])

def test_parse_unknown():
    p = ExcellonParser(FileSettings())
    p._parse('Not A Valid Statement')
    assert_equal(p.statements[0].stmt, 'Not A Valid Statement')


