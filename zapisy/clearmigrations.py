import os

i = 0
for root, subdir, files in os.walk("."):
    if "migrations" in root:
        for migfile in files:
            if migfile != "__init__.py":
                fpath = os.path.join(root, migfile)
                print("removing %s" % fpath)
                os.remove(fpath)
                i += 1

print("%d files removed" % i)
