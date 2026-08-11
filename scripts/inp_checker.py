#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inp_checker.py — Static check of Abaqus .inp files
===================================================
Standalone Python 3 tool. Catches common input-file mistakes BEFORE submitting a
job: missing *End Step, materials used but not defined, sections without material,
suspicious units (density in kg/m^3, modulus in Pa), duplicate keywords, etc.

Usage:
    python3 inp_checker.py Job-1.inp
    python3 inp_checker.py Job-1.inp --quiet

Exit code: 0 = no problems found, 1 = problems found.
Note: this is a static heuristic check — it cannot replace the Abaqus
consistency check (`abaqus job=... check`).
"""

import sys
import re
import argparse

KEYWORDS = re.compile(r'^\*([A-Za-z][A-Za-z0-9 ,=._()/\-]*?)'
                      r'(?:\s*,|$)', re.IGNORECASE)


def parse_inp(path):
    """Return list of (keyword, line_no, raw_line, body_lines)."""
    sections = []
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    cur = None
    for i, raw in enumerate(lines, 1):
        line = raw.strip()
        if line.startswith('**') or not line:
            continue
        m = KEYWORDS.match(line)
        if m:
            cur = {'kw': m.group(1).strip().lower().split(',')[0].strip(),
                   'line': i, 'raw': line, 'body': []}
            sections.append(cur)
        elif cur is not None:
            cur['body'].append(line)
    return sections


def main():
    p = argparse.ArgumentParser(description='Static .inp checker')
    p.add_argument('inp', help='path to the .inp file')
    p.add_argument('--quiet', action='store_true', help='only print problems')
    args = p.parse_args()

    try:
        sections = parse_inp(args.inp)
    except FileNotFoundError:
        print(f'ERROR: file not found: {args.inp}', file=sys.stderr)
        return 1

    problems = []
    warns = []
    kws = [s['kw'] for s in sections]
    nsteps = kws.count('step')
    nend = kws.count('end step')

    # 1. Structure
    if nsteps == 0:
        problems.append('no *Step found')
    elif nsteps != nend:
        problems.append(f'{nsteps} *Step but {nend} *End Step')

    # 2. Materials defined vs used
    materials = set()
    for s in sections:
        if s['kw'] == 'material':
            # name=... or bare name after comma
            m = re.search(r'name\s*=\s*([^,]+)', s['raw'], re.I)
            if m:
                materials.add(m.group(1).strip())
            elif len(s['raw'].split(',')) >= 2:
                materials.add(s['raw'].split(',')[1].strip())
    used = set()
    for s in sections:
        if s['kw'] in ('solid section', 'shell section', 'beam section',
                       'composite shell section', 'surface section'):
            m = re.search(r'material\s*=\s*([^,]+)', s['raw'], re.I)
            if m:
                used.add(m.group(1).strip())
    for u in used:
        if u and u not in materials:
            problems.append(f'section references undefined material "{u}"')

    # 3. Unit heuristics (N-mm-MPa project standard)
    for s in sections:
        if s['kw'] == 'density':
            for b in s['body'][:1]:
                v = b.split(',')[0].strip()
                try:
                    fv = float(v)
                    if 1.0 < fv < 1.0e4:
                        warns.append(f'line {s["line"]}: density {fv} looks like kg/m^3 '
                                     '— in N-mm-MPa use tonne/mm^3 (e.g. 7.85e-9)')
                except ValueError:
                    pass
        if s['kw'] in ('elastic', 'user material'):
            for b in s['body'][:1]:
                v = b.split(',')[0].strip()
                try:
                    fv = float(v)
                    if fv > 5.0e5:
                        warns.append(f'line {s["line"]}: modulus/constant {fv:g} looks '
                                     'like Pa — in N-mm-MPa use MPa (e.g. 210000)')
                except ValueError:
                    pass
        if s['kw'] == 'specific heat':
            for b in s['body'][:1]:
                v = b.split(',')[0].strip()
                try:
                    fv = float(v)
                    if 100.0 < fv < 1.0e5:
                        warns.append(f'line {s["line"]}: specific heat {fv} looks like '
                                     'J/(kg*K) — in N-mm-MPa use x1e6 (N*mm/(tonne*K))')
                except ValueError:
                    pass
        if s['kw'] == 'film':
            for b in s['body'][:1]:
                v = b.split(',')[1].strip() if ',' in b else ''
                try:
                    fv = float(v)
                    if 1.0e-5 <= fv <= 1.0e-4:
                        warns.append(f'line {s["line"]}: film coefficient {fv:g} looks '
                                     'like a 1e-6-style error — W/(m^2*K) -> mW/(mm^2*K) x1e-3')
                except ValueError:
                    pass

    # 4. Duplicate node/element definitions
    if kws.count('node') > 1 and kws.count('element') > 1:
        warns.append('multiple *Node/*Element blocks — check for accidental duplicates')

    # 5. Element types sanity
    elem_blocks = [s for s in sections if s['kw'] == 'element']
    for s in elem_blocks:
        if 'C3D8' in s['raw'] and 'C3D8I' not in s['raw'] and 'C3D8R' not in s['raw']:
            warns.append(f'line {s["line"]}: fully-integrated C3D8 in bending — '
                         'consider C3D8R/C3D8I (shear locking)')

    # Output
    for w in warns:
        if not args.quiet:
            print(f'WARNING: {w}')
    for x in problems:
        print(f'ERROR:   {x}')

    if not args.quiet:
        print(f'--- {len(sections)} keyword sections, '
              f'{len(problems)} errors, {len(warns)} warnings')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
