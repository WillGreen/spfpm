#!/usr/bin/python3
# Demonstration of Simple Python Fixed-Point Module
# (C)Copyright 2006-2017, RW Penney

import argparse, time
from collections import OrderedDict
try:
    import matplotlib, numpy
    import matplotlib.pyplot as plt
    HAVE_MATPLOTLIB = True
except ImportError:
    HAVE_MATPLOTLIB = False

import FixedPoint


def basicDemo():
    """Basic demonstration of roots & exponents at various accuracies"""

    for resolution in [8, 32, 80, 274]:
        family = FixedPoint.FXfamily(resolution)
        val = 2

        print('=== {0} bits ==='.format(resolution))
        rt = FixedPoint.FXnum(val, family).sqrt()
        print('sqrt(' + str(val) + ')~ ' + str(rt))
        print('sqrt(' + str(val) + ')^2 ~ ' + str(rt * rt))
        print('exp(1) ~ ' + str(family.exp1))
        print()


def overflowDemo():
    """Illustrate how finite range limits calculation of exponents"""

    res = 20
    print('=== {0}-bit fractional part ==='.format(res))
    for intsize in [4, 8, 16, 32]:
        family = FixedPoint.FXfamily(res, intsize)
        x = FixedPoint.FXnum(0.0, family)
        step = 0.1
        while True:
            try:
                ex = x.exp()
            except FixedPoint.FXoverflowError:
                print('{0:2d}-bit integer part: exp(x) overflows near x={1:.3g}'.format(intsize, float(x)))
                break
            x += step
    print()


def speedDemo():
    """calculate indicative speed of floating-point operations"""

    print('=== speed test ===')
    for res, count in [ (16, 10000), (32, 10000),
                        (64, 10000), (128, 10000),
                        (256, 10000), (512, 10000) ]:
        fam = FixedPoint.FXfamily(res)
        x = FixedPoint.FXnum(0.5, fam)
        lmb = FixedPoint.FXnum(3.6, fam)
        one = FixedPoint.FXnum(1.0, fam)
        t0 = time.clock()
        for i in range(count):
            # use logistic-map in chaotic region:
            x = lmb * x * (one - x)
        t1 = time.clock()
        ops = count * 3
        Dt = t1 - t0
        print('{0} {1}-bit arithmetic operations in {2:.2f}s ~ {3:.2g} FLOPS' \
                .format(ops, res, Dt, (ops / Dt)))

    for res, count in [ (4, 10000), (8, 10000), (12, 10000),
                        (24, 10000), (48, 10000), (128, 10000),
                        (512, 10000) ]:
        fam = FixedPoint.FXfamily(res, 4)
        x = FixedPoint.FXnum(2, fam)
        t0 = time.clock()
        for i in range(count):
            y = x.sqrt()
        t1 = time.clock()
        Dt = (t1 - t0)
        print('{} {}-bit square-roots in {:.3g}s ~ {:.3g}/ms' \
                .format(count, res, Dt, count*1e-3/Dt))


def piPlot():
    """Plot graph of approximations to Pi"""

    b_min, b_max = 8, 25
    pi_true = FixedPoint.FXfamily(b_max + 40).pi
    pipoints = []
    for res in range(b_min, b_max+1):
        val = 4 * FixedPoint.FXnum(1, FixedPoint.FXfamily(res)).atan()
        pipoints.append([res, val])
    pipoints = numpy.array(pipoints)
    truepoints = numpy.array([[b_min, pi_true], [b_max, pi_true]])

    plt.xlabel('bits')
    plt.ylabel(r'$4 tan^{-1}1$')
    plt.xlim([b_min, b_max])
    plt.ylim([3.13, 3.16])
    plt.grid(True)
    for arr, style in ((truepoints, '--'), (pipoints, '-')):
        plt.plot(arr[:,0], arr[:,1], ls=style)
    plt.show()


def piAccuracyPlot():
    """Plot graph of fractional bits wasted due to accumulated roundoff."""

    def lostbits(x, x_acc):
        fam_acc = x_acc.family
        eps = (FixedPoint.FXnum(x, fam_acc) - x_acc)
        return (abs(eps).log() / fam_acc.log2
                    + x.family.resolution)

    losses = []
    for bits in range(4, 500, 4):
        fam_acc = FixedPoint.FXfamily(bits + 40)
        fam = FixedPoint.FXfamily(bits)
        pi_true = fam_acc.pi
        pi_family = fam.pi
        atan = 4 * FixedPoint.FXnum(1, fam).atan()
        losses.append((bits, lostbits(atan, pi_true),
                             lostbits(pi_family, pi_true)))
    losses = numpy.array(losses)

    plt.xlabel('resolution bits')
    plt.ylabel('error bits')
    plt.grid(True)
    plt.plot(losses[:,0], losses[:,1], label=r'$4 tan^{-1} 1$')
    plt.plot(losses[:,0], losses[:,2], label=r'$\pi_{family}$')
    plt.legend(loc='best', fontsize='small')
    plt.show()


def main():
    demos = OrderedDict([
        ('basic',       basicDemo),
        ('overflow',    overflowDemo),
        ('speed',       speedDemo) ])
    if HAVE_MATPLOTLIB:
        demos['piplot'] = piPlot
        demos['piaccplot'] = piAccuracyPlot

    parser = argparse.ArgumentParser(
                description='Rudimentary demonstrations of'
                            ' the Simple Python Fixed-point Module (SPFPM)')
    parser.add_argument('-a', '--all', action='store_true')
    parser.add_argument('demos', nargs='*',
            help='Demo applications ({})'.format('/'.join(demos.keys())))
    args = parser.parse_args()

    if args.all or not args.demos:
        args.demos = list(demos.keys())

    for demoname in args.demos:
        demos[demoname]()


if __name__ == "__main__":
    main()

# vim: set ts=4 sw=4 et:
