#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
odb_extract.py — CLI result extraction from Abaqus .odb files
==============================================================
Runs INSIDE the Abaqus Python environment (needs odbAccess):
    abaqus python odb_extract.py Job-1.odb --field U --max
    abaqus python odb_extract.py Job-1.odb --field S --max
    abaqus python odb_extract.py Job-1.odb --field RF --set Fixed-End
    abaqus python odb_extract.py Job-1.odb --history U2 --region "Node BEAM-1.5"
    abaqus python odb_extract.py Job-1.odb --energy

Exit code: 0 = ok.
"""

import sys
import argparse

try:
    from odbAccess import openOdb
except ImportError:
    print('ERROR: this script must run inside Abaqus Python:\n'
          '    abaqus python odb_extract.py ...', file=sys.stderr)
    sys.exit(1)


def _last_frame(odb, step):
    return odb.steps[step].frames[-1]


def field_max(odb, step, field_key, component=None):
    frame = _last_frame(odb, step)
    if field_key not in frame.fieldOutputs:
        print(f'field output "{field_key}" not in step {step}')
        return 1
    f = frame.fieldOutputs[field_key]
    best = None
    for v in f.values:
        d = v.data
        if component is not None:
            if component >= len(d):
                continue
            val = d[component]
        else:
            val = max(abs(x) for x in d)
        if best is None or val > best[0]:
            best = (val, v.elementLabel, v.integrationPoint,
                    v.nodeLabel, v.sectionPoint)
    print(f'{field_key}{"/"+str(component) if component is not None else ""} '
          f'max = {best[0]:.6g}')
    print(f'  at element={best[1]} ip={best[2]} node={best[3]} sp={best[4]}')
    return 0


def field_on_set(odb, step, field_key, set_name):
    frame = _last_frame(odb, step)
    if field_key not in frame.fieldOutputs:
        print(f'field output "{field_key}" not in step {step}')
        return 1
    f = frame.fieldOutputs[field_key]
    inst = odb.rootAssembly.instances
    region = None
    for name in inst.keys():
        if set_name in inst[name].nodeSets:
            region = inst[name].nodeSets[set_name]
            break
        if set_name in inst[name].elementSets:
            region = inst[name].elementSets[set_name]
            break
    if region is None and set_name in odb.rootAssembly.nodeSets:
        region = odb.rootAssembly.nodeSets[set_name]
    if region is None:
        print(f'set "{set_name}" not found')
        return 1
    sub = f.getSubset(region=region)
    total = [0.0] * max((len(v.data) for v in sub.values), default=0)
    for v in sub.values:
        for i, x in enumerate(v.data):
            total[i] += x
    print(f'{field_key} on "{set_name}": sum = {total}')
    return 0


def history(odb, step, var, region_key):
    if step not in odb.steps:
        print(f'step {step} not found')
        return 1
    regions = odb.steps[step].historyRegions
    if region_key and region_key not in regions:
        print(f'history region "{region_key}" not found. Available:')
        for k in regions.keys():
            print('  ', k)
        return 1
    region = regions[region_key] if region_key else next(iter(regions.values()))
    if var not in region.historyOutputs:
        print(f'history output "{var}" not in {region_key}. Available:')
        for k in region.historyOutputs.keys():
            print('  ', k)
        return 1
    h = region.historyOutputs[var]
    print(f'{var} on {region_key}: {len(h.data)} points, last = '
          f'{h.data[-1].value:.6g} at time {h.data[-1].frameValue:.6g}')
    return 0


def energy(odb, step):
    if step not in odb.steps:
        print(f'step {step} not found')
        return 1
    region = odb.steps[step].historyRegions.get('Assembly ASSEMBLY')
    if region is None:
        print('no Assembly ASSEMBLY history region (need global history output)')
        return 1
    keys = region.historyOutputs
    last = lambda k: keys[k].data[-1].value if k in keys else None
    for k in ('ALLIE', 'ALLKE', 'ALLAE', 'ALLVD', 'ALLWK', 'ETOTAL', 'ALLPD'):
        v = last(k)
        if v is not None:
            print(f'{k} = {v:.6e}')
    ie, ke = last('ALLIE'), last('ALLKE')
    if ie and ke and ie > 0:
        print(f'ALLKE/ALLIE = {ke/ie:.3%}')
    ae = last('ALLAE')
    if ie and ae:
        print(f'ALLAE/ALLIE = {ae/ie:.3%}  (hourglass; target <5%)')
    return 0


def main():
    p = argparse.ArgumentParser(description='Extract results from an Abaqus ODB')
    p.add_argument('odb')
    p.add_argument('--step', default=None, help='step name (default: last step)')
    p.add_argument('--field', help='field output key, e.g. U, S, RF, PEEQ')
    p.add_argument('--max', action='store_true', help='report max value')
    p.add_argument('--component', type=int, default=None,
                   help='component index for max (default: max abs any comp)')
    p.add_argument('--set', help='node/element set name (sum over set)')
    p.add_argument('--history', help='history output variable, e.g. U2, RF1')
    p.add_argument('--region', default=None, help='history region key')
    p.add_argument('--energy', action='store_true', help='global energy diagnostics')
    args = p.parse_args()

    odb = openOdb(path=args.odb, readOnly=True)
    steps = list(odb.steps.keys())
    step = args.step if args.step else steps[-1]
    print(f'odb: {args.odb}  steps: {steps}  using: {step}')

    if args.field:
        if args.set:
            field_on_set(odb, step, args.field, args.set)
        else:
            field_max(odb, step, args.field, args.component)
    if args.history:
        history(odb, step, args.history, args.region)
    if args.energy:
        energy(odb, step)
    if not (args.field or args.history or args.energy):
        p.print_help()
    odb.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
