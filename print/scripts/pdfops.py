"""Minimal PDF content-stream tokenizer and top-level q/Q grouping."""
import re

DELIM = b'()<>[]{}/%'
WS = b' \t\r\n\x0c\x00'
BACKSLASH = 92


def tokens(s):
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c in WS:
            i += 1
        elif c == ord('%'):
            while i < n and s[i] not in (10, 13):
                i += 1
        elif c == ord('('):
            j, depth = i + 1, 1
            while j < n and depth:
                ch = s[j]
                if ch == BACKSLASH:
                    j += 2
                    continue
                depth += (ch == ord('(')) - (ch == ord(')'))
                j += 1
            yield ('str', i, j)
            i = j
        elif c == ord('<') and s[i+1:i+2] == b'<':
            yield ('dict<', i, i + 2)
            i += 2
        elif c == ord('>') and s[i+1:i+2] == b'>':
            yield ('dict>', i, i + 2)
            i += 2
        elif c == ord('<'):
            j = s.index(b'>', i)
            yield ('hex', i, j + 1)
            i = j + 1
        elif c in b'[]{}':
            yield ('delim', i, i + 1)
            i += 1
        elif c == ord('/'):
            j = i + 1
            while j < n and s[j] not in WS and s[j] not in DELIM:
                j += 1
            yield ('name', i, j)
            i = j
        else:
            j = i
            while j < n and s[j] not in WS and s[j] not in DELIM:
                j += 1
            if j == i:
                j += 1
            w = s[i:j]
            if re.fullmatch(rb'[+-]?(\d+\.?\d*|\.\d+)', w):
                yield ('num', i, j)
            else:
                yield ('op', i, j)
                if w == b'ID':               # inline image data runs to EI
                    k = s.index(b'EI', j)
                    yield ('data', j, k)
                    i = k
                    continue
            i = j


def top_groups(s):
    """Byte spans (start, end) of each top-level q...Q group, and loose ops."""
    out, depth, start, loose = [], 0, None, []
    for kind, a, b in tokens(s):
        if kind != 'op':
            continue
        w = s[a:b]
        if w == b'q':
            if depth == 0:
                start = a
            depth += 1
        elif w == b'Q':
            depth -= 1
            if depth == 0:
                out.append((start, b))
        elif depth == 0:
            loose.append((a, b, w))
    return out, loose
