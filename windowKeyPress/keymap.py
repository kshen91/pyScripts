# -*- coding: utf-8 -*-
# Author: cylisery@outlook.com

key_mapping = {
    '`'   : 'grave',
    '~'   : 'asciitilde',
    '!'   : 'exclam',
    '@'   : 'at',
    '#'   : 'numbersign',
    '$'   : 'dollar',
    '%'   : 'percent',
    '^'   : 'asciicircum',
    '&'   : 'ampersand',
    '*'   : 'asterisk',
    '('   : 'parenleft',
    ')'   : 'parenright',
    '-'   : 'minus',
    '_'   : 'underscore',
    '='   : 'equal',
    '+'   : 'plus',
    '['   : 'bracketleft',
    '{'   : 'braceleft',
    ']'   : 'bracketright',
    '}'   : 'braceright',
    ';'   : 'semicolon',
    ':'   : 'colon',
    "'"   : 'apostrophe',
    '"'  : 'quotedbl',
    ','   : 'comma',
    '<'   : 'less',
    '.'   : 'period',
    '>'   : 'greater',
    '/'   : 'slash',
    '?'   : 'question',
    '\\'  : 'backslash',
    '|'   : 'bar',
    ' '   : 'space',
    'esc' : 'Escape',
    'Esc' : 'Escape',
    '\n'  : 'Return',

    'shift' : 'Shift_L',
    'ctrl'  : 'Control_L',
    'alt'   : 'Alt_L',
    'caps'  : 'Caps_Lock'
}

def NeedShift(key):
    need_shift = '~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:"ZXCVBNM<>?'
    return (key in need_shift)
