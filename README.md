These are some Python scripts that I've made for things. Specifically, these ones were useful enough to make it into my `~/bin`. I like them.

If you don't know how to do any of the things I've done here, you might be better off doing them yourself instead. But my scripts are pretty.

Just for fun, a word about SELF. Try:

`$ diff SELF <(./SELF)`

This is a bit cleaner than

`$ diff SELF <(python SELF)`

because the Python interpreter won't complain about blank files, so you get the trivial solution:

    $ touch TRIVIAL
    $ diff TRIVIAL <(python TRIVIAL)

Passing `--side-by-side` to `diff` will also help you catch any rascals who try to pass off a blank self-quine.
... In case you're worried about that.
