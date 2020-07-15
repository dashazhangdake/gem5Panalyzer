from pathlib import Path
import os


class PreProcessing:
    def __init__(self, filename, tracepath):
        self.fname = filename
        self.tracedir = tracepath

    def preprocessing(self, delete=1):
        # Initialize Path variables
        trace_dir = self.tracedir
        trace_path = trace_dir / (self.fname + '.txt')
        trace_path_o = trace_dir / (self.fname + '_p' + '.txt')
        fin = open(trace_path, 'rt')
        fout = open(trace_path_o, 'wt')

        for line in fin:
            fout.write(line.replace('fp', 'r11').replace('sp', 'r13').replace('lr', 'r14').replace('pc', 'r15'))
        fin.close()
        if delete == 1:
            os.remove(trace_path)  # remove the original_trace

    def osrenaming(self):
        # Initialize Path variables
        trace_dir = self.tracedir
        trace_path = trace_dir / (self.fname + '.txt')
        trace_path_o = trace_dir / (self.fname + '_p' + '.txt')
        os.rename(trace_path_o, trace_path)


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    tracedir = base_dir.joinpath('../TraceDir')
    PreProcessing('prime', tracedir).preprocessing()
    PreProcessing('prime', tracedir).osrenaming()
