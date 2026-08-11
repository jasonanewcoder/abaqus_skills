#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
unit_converter.py — Abaqus unit-system conversion & validation
================================================================
Standalone Python 3 tool (runs OUTSIDE Abaqus). Converts quantities between the
project standard N-mm-MPa system and SI, and validates that a value is plausible
for a given physical quantity in N-mm-MPa.

Usage:
    python3 unit_converter.py --to-abaqus density 7850
    python3 unit_converter.py --to-abaqus specific_heat 460
    python3 unit_converter.py --to-abaqus convection 15
    python3 unit_converter.py --to-si stress 210000
    python3 unit_converter.py --validate density 7.85e-9
    python3 unit_converter.py --list

Exit code: 0 = ok, 1 = unknown quantity, 2 = validation failed.
"""

import sys
import argparse

# (name, abaqus_unit, si_unit, si_to_abaqus_factor)
QUANTITIES = {
    'length':       ('mm',        'm',         1e-3),
    'force':        ('N',         'N',         1.0),
    'stress':       ('MPa',       'Pa',        1e-6),     # 1 Pa = 1e-6 MPa
    'pressure':     ('MPa',       'Pa',        1e-6),
    'elastic_modulus': ('MPa',    'Pa',        1e-6),
    'density':      ('tonne/mm^3','kg/m^3',    1e-12),    # 1 kg/m^3 = 1e-12 tonne/mm^3
    'gravity':      ('mm/s^2',    'm/s^2',     1e3),      # 1 m/s^2 = 1e3 mm/s^2
    'velocity':     ('mm/s',      'm/s',       1e3),
    'acceleration': ('mm/s^2',    'm/s^2',     1e3),
    'specific_heat': ('N*mm/(tonne*K)', 'J/(kg*K)', 1e6), # 1 J/(kg*K) = 1e6
    'thermal_conductivity': ('mW/(mm*K)', 'W/(m*K)', 1.0),# value unchanged
    'convection':   ('mW/(mm^2*K)', 'W/(m^2*K)', 1e-3),   # 1 W/m^2K = 1e-3 mW/mm^2K
    'heat_flux':    ('mW/mm^2',   'W/m^2',     1e-3),
    'heat_generation': ('mW/mm^3','W/m^3',     1e-3),
    'energy':       ('N*mm',      'J',         1e3),      # 1 J = 1e3 N*mm
    'power':        ('mW',        'W',         1e3),      # 1 W = 1e3 mW
    'latent_heat':  ('N*mm/tonne','J/kg',      1e6),
    'mass':         ('tonne',     'kg',        1e-3),
}


def to_abaqus(name, si_value):
    q = QUANTITIES[name]
    return si_value * q[2]


def to_si(name, abaqus_value):
    q = QUANTITIES[name]
    return abaqus_value / q[2]


def validate(name, abaqus_value):
    """Heuristic sanity ranges for common quantities in N-mm-MPa."""
    ranges = {
        'density': (1e-10, 1e-5),          # tonne/mm^3 (gases..heavy metals)
        'stress': (1e-3, 1e4),             # MPa
        'elastic_modulus': (1e3, 5e5),     # MPa
        'specific_heat': (1e6, 1e9),       # N*mm/(tonne*K)
        'thermal_conductivity': (1e-2, 1e3),  # mW/(mm*K)
        'convection': (1e-4, 1e-1),        # mW/(mm^2*K)
        'gravity': (9e3, 1e4),             # mm/s^2
        'length': (1e-4, 1e5),             # mm
        'force': (1e-3, 1e9),              # N
        'energy': (1e-3, 1e12),            # N*mm
    }
    if name not in ranges:
        return True, 'no range defined'
    lo, hi = ranges[name]
    ok = lo <= abaqus_value <= hi
    msg = f'in range [{lo:g}, {hi:g}]' if ok else f'OUT of range [{lo:g}, {hi:g}]'
    return ok, msg


def main():
    # Accept "--to-abaqus" / "-to-abaqus" / "to-abaqus" styles on the CLI
    args0 = [a[2:] if a.startswith('--') else a for a in sys.argv[1:]]

    p = argparse.ArgumentParser(description='Abaqus N-mm-MPa unit converter')
    p.add_argument('mode',
                   choices=['to-abaqus', 'to-si', 'validate', 'list'],
                   metavar='MODE', help='--to-abaqus | --to-si | --validate | --list')
    p.add_argument('quantity', nargs='?', help='physical quantity name')
    p.add_argument('value', nargs='?', type=float, help='numeric value')
    args = p.parse_args(args0)

    if args.mode == 'list':
        for name, (au, su, f) in sorted(QUANTITIES.items()):
            print(f'{name:<24} abaqus={au:<18} si={su:<12} si->abaqus x{f:g}')
        return 0

    if args.quantity not in QUANTITIES:
        print(f'ERROR: unknown quantity "{args.quantity}". Use --list.', file=sys.stderr)
        return 1
    if args.value is None:
        print('ERROR: missing value', file=sys.stderr)
        return 1

    q = QUANTITIES[args.quantity]
    if args.mode == 'to-abaqus':
        v = to_abaqus(args.quantity, args.value)
        print(f'{args.value:g} {q[1]} = {v:g} {q[0]}  (factor x{q[2]:g})')
        ok, msg = validate(args.quantity, v)
        print(f'plausibility: {msg}')
        return 0 if ok else 2
    elif args.mode == 'to-si':
        v = to_si(args.quantity, args.value)
        print(f'{args.value:g} {q[0]} = {v:g} {q[1]}  (factor /{q[2]:g})')
        return 0
    else:  # validate
        ok, msg = validate(args.quantity, args.value)
        print(f'{args.value:g} {q[0]} : {msg}')
        return 0 if ok else 2


if __name__ == '__main__':
    sys.exit(main())
