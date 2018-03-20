import argparse

def collatz(n, verbose=False):
    """Return 1 if n is not a counterexample to the Collatz / Ulam / Kakutani /
    Thwaites / blah / etc conjecture.  Otherwise return some other number, or
    never return.

    Oh, and also return the number of steps taken to reduce the input.
    """
    if verbose:
        vprint = lambda x: print(x)
    else:
        vprint = lambda x: None
    steps = 0
    while n > 1:
        steps += 1
        vprint(n)
        if n % 2:
            n = 3 * n + 1
        else:
            n = n // 2
    return (n, steps)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Toy based on the 3n+1 conjecture.")

    parser.add_argument("number", type=int, help="positive integer to test")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Print intermediate values")
    args = parser.parse_args()
    print(collatz(args.number, verbose=args.verbose))
