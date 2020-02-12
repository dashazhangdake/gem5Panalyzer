from pathlib import Path


def preprocessing(fname, tracedir):
    # Initialize Path variables
    trace_dir = tracedir
    trace_path = trace_dir / (fname + '.txt')
    trace_path_o = trace_dir / (fname + '_p' + '.txt')
    fin = open(trace_path, 'rt')
    fout = open(trace_path_o, 'wt')

    for line in fin:
        fout.write(line.replace('fp', 'r11').replace('sp', 'r13').replace('lr', 'r14').replace('pc', 'r15'))
    fin.close()


if __name__ == "__main__":
    preprocessing('prime')
