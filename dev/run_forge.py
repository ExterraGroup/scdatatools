from scdatatools.forge import DataCoreBinary

count = 0


def run_forge():
    global count
    import time

    dcf = "research/Game.dcb.3.9.0-live.5125346"
    print(f"\n\nLoading {dcf}")
    print("-" * 80)

    start = time.process_time()
    f = DataCoreBinary(dcf)
    end = time.process_time()
    print(f"Loaded DCB in {end-start}s")
    print(f"\nReading every property on every record...")
    print("-" * 80)

    def _iter_props(r):
        global count
        count += 1
        if hasattr(r, "properties"):
            [_iter_props(_) for _ in r.properties]

    try:
        # print_records(f)
        start = time.process_time()
        for r in f.records:
            # print(f'{r.type}:{r.name} - {r.filename}')
            count += 1
            _iter_props(r)
    finally:
        end = time.process_time()
        print(f"# Records: {len(f.records)} ")
        print(f"# properties traversed: {count}")
        print(f"Total Time: {end-start}s")


run_forge()