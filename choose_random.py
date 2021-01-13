#!/usr/bin/env python3

import random
import sys

if __name__ == "__main__":
    options = list(sys.stdin)  # list of lines of text
    print(random.choice(options), end='')
