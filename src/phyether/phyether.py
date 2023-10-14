try:
    import .util
except FileNotFoundError:
    # TODO: Couldn't find ngspice library, do something (disable simulation?)
    raise


def main():
    print("Starting phyether...")
