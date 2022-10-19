import sys
import time as timemodule

TIMEMEM   = None
UPDATEMEM = None
TEXTMEM   = None

def inline(x, X, N=50, prefix="", suffix = "", done = "Done", stdout=True, time=True, autoupdate=0):
    """
    Base progress bar function.
    Finishes when x == X.
    ---
    x      : Current advancement
    X      : Final advancement
    N      : Bar length
    prefix : bar prefix
    suffix : bar suffix
    """
    global TIMEMEM
    global UPDATEMEM
    global TEXTMEM

    update = (x >= X) # Force update if progress is 100%
    if time or autoupdate :
        T = timemodule.time()
        if TIMEMEM is None:
            TIMEMEM = T
        if UPDATEMEM is None:
            UPDATEMEM = T
    if autoupdate:
        dt = T - UPDATEMEM
        if dt > autoupdate:
            update |= True
            UPDATEMEM = T
        else:
            update |= False
    else:
        update |= True
    if update:
        if x > X:
            x = X
        k = int(N * (x/X)) if X > 0 else N
        bar = "#" * k + " " * (N - k)
        count = f"({x+1}/{X+1})"
        if time:
            tpx = (T-TIMEMEM) / x if x > 0 else 0
            remx = X-x
            rems = remx * tpx
            remaining = f"(ETR: {rems:.2f} s)"
            text = f"\r{prefix} |{bar}| {count} {remaining} {suffix}"
        else:
            text = f"\r{prefix} |{bar}| {count} {suffix}"
        TEXTMEM = text
        if x >= X:
            if time:
                dt = T - TIMEMEM
                text += f" - {done} in {dt:.3f} s\n"
                TIMEMEM = None
            else:
                text += f" - {done}\n"
    else:
        text = TEXTMEM
    if stdout and update:
        sys.stdout.write(text)
    return text

def inlineCycles(i, I, *args, **kwargs):
    """
    Progress bar to keep track of a given number of cycles (eg. for loop).
    i starts at 0
    Finishes when i+1 == I
    ---
    i      : Current cycle (starting at 0)
    I      : Total number of cycles
    N      : Bar length
    prefix : bar prefix
    suffix : bar suffix
    """
    inline(i, I-1, *args, **kwargs)

def test(N=1_000_000):
    import time
    t0 = time.time()
    for i in range(N):
        pass
    t1 = time.time()
    print(f"Without progressbar : {t1-t0:.4f} s ({1e6*(t1-t0)/N:.4f} µs/cycle)")

    t0 = time.time()
    for i in range(N):
        inlineCycles(i, N, prefix="Testing", autoupdate=0.1)
    t1 = time.time()
    print(f"With progressbar (autoupdate=0.1) : {t1-t0:.4f} s ({1e6*(t1-t0)/N:.4f} µs/cycle)")

    t0 = time.time()
    for i in range(N):
        inlineCycles(i, N, prefix="Testing", autoupdate=0.2)
    t1 = time.time()
    print(f"With progressbar (autoupdate=0.2) : {t1-t0:.4f} s ({1e6*(t1-t0)/N:.4f} µs/cycle)")

    t0 = time.time()
    for i in range(N):
        inlineCycles(i, N, prefix="Testing", autoupdate=1.0)
    t1 = time.time()
    print(f"With progressbar (autoupdate=1.0) : {t1-t0:.4f} s ({1e6*(t1-t0)/N:.4f} µs/cycle)")
