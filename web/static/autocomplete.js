/*
Attach event handler to any control with given tag.

When control has keypress,
    start a timer.

when control loses focus,
    turn off timer

When timer elapses:
    check if control still has focus,
        if not, exit
    check content against cache
        if in cache,
            use those values for suggestion list.
            exit
        if not in cache,
            call api passing in the terms and source.
            if valid response,
                add those values to cache
                use those values for suggestion list.
                exit
            if not a valid response,
                ? should clear suggestion list?
                exit
 */