import sys

def uncollatz(n, depth, visit=print, skip=lambda x: False):
    if skip(n, depth):
        return
    visit(n, depth)
    if depth <= 0:
        return
    uncollatz(2*n, depth-1, visit=visit, skip=skip)
    if n % 3 == 1:
        odd = n // 3
        if odd % 2:
            uncollatz(n // 3, depth-1, visit=visit, skip=skip)

if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].isdecimal():
        print(("Pass a number N, and I'll print all the numbers from which"
               " 1 is reached within N Collatz steps"), file=sys.stderr)
        sys.exit(1)
    numbers = {}
    max_depth = int(sys.argv[1])
    uncollatz(1, max_depth, visit=numbers.__setitem__,
              skip=(lambda x, d: x in numbers))
    for n, depth in sorted(numbers.items(), key=lambda p: p[0]):
        print("{}\t{}".format(n, max_depth - depth))
