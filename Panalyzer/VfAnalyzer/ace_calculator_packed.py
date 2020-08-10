import numpy as np
from pathlib import Path
from Panalyzer.TraceParser.csv2np import csv2np
from Panalyzer.VfAnalyzer.analyzer_core import AvfAnalyzer


class ace_calculators:
    def __init__(self, file_in, reg_count):
        self.fin = file_in
        self.reg_num = reg_count

    def ace_calculator_detailed(self, start, length, sample_ratio):
        reg_n = self.reg_num
        info = csv2np(self.fin, start, length, self.reg_num).arm32detailed()

        wr_hist = info['wr']
        t_hist = info['tick']
        m_hist = info['masking']

        window_size = length

        sample_count = int(sample_ratio * window_size)
        ace_current_window = np.zeros([reg_n + 1, sample_count], dtype=np.int64)
        for i in range(reg_n):
            ace_ith_temp = AvfAnalyzer(wr_hist[i, :, :], t_hist, m_hist[i, :]).ace_calculator_wr()[1, :]
            sample_idx = np.random.choice(window_size, sample_count)
            sampled_ace_ith = ace_ith_temp[sample_idx]
            ace_current_window[i, :] = sampled_ace_ith

            # Reorder ace current window
            ace_current_window[i, -1] = ace_ith_temp[-1]
            ace_current_window[-1, :] = t_hist[sample_idx]
            ace_current_window[-1, -1] = t_hist[-1]
            ace_current_window = np.sort(ace_current_window, axis=1, kind='mergesort')

        return ace_current_window


if __name__ == "__main__":
    reg_num = 16
    project_dir = Path(__file__).resolve().parent.parent
    csv_dir = project_dir.joinpath('tempcsv')
    fname = "prime.csv"
    # T = csv2np(csv_dir / fname, 0, 1000, 16).arm32detailed()
    # details = csv2np(csv_dir / fname, 0, 1000, 16).arm32detailed()
    # print(len(details['tick']))
    ace_test = ace_calculators(csv_dir / fname, reg_num).ace_calculator_detailed(1000, 100, sample_ratio=0.1)
    print(ace_test)
    print(np.shape(ace_test))
