import glob
import errno

path = 'data/*.data'
files = glob.glob(path)
output = open('output.table', 'w')
total = {}
number = {}
for x in ('h0', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
    for y in ('h0', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
        total[(x, y)] = 0
        number[(x, y)] = 0

for name in files: # 'file' is a builtin type, 'name' is a less-ambiguous variable name.
    #print name + "\n\n"
    try:
        with open(name) as f: # No need to specify 'r': this is the default.
            # sys.stdout.write(f.read())
            line = f.readline()
            while( line != ""):
                args = line.split()
                #for arg in args:
                #    print arg
                server = args[0]
                if(args[4] == "10.0.0.1"):
                    client = 'h0'
                if(args[4] == "10.0.0.2"):
                    client = 'h1'
                if(args[4] == "10.0.0.3"):
                    client = 'h2'
                if(args[4] == "10.0.0.4"):
                    client = 'h3'
                if(args[4] == "10.0.0.5"):
                    client = 'h4'
                if(args[4] == "10.0.0.6"):
                    client = 'h5'
                if(args[4] == "10.0.0.7"):
                    client = 'h6'
                speed = float(args[2])
                total[(server, client)] = total[(server, client)] + speed
                number[(server, client)] = number[(server, client)] + 1
                line = f.readline()
    except IOError as exc:
        if exc.errno != errno.EISDIR: # Do not fail if a directory is found, just ignore it.
            raise # Propagate other kinds of IOError.
    #for (x, y) in total:
    #    print total[(x, y)]

for x in ('h0', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
    output.write("\n\\hline\n")
    for y in ('h0', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
        if(number[(x, y)] != 0):
            # print total[(x,y)]
            output.write(" " + str("{0:.2f}".format(float(total[(x,y)])/float(number[(x,y)]))) + " ")
        else:
            output.write(" 0.00 ")
        if y not in ("h6"):
            output.write(" & ")
output.write("\n\\hline")

output.close()

