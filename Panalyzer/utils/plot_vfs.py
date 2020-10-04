import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


def plot(filename):
    # Setup raw trace file Paths
    top_dir = Path(__file__).resolve().parent.parent.parent
    project_dir = Path(__file__).resolve().parent / 'Panalyzer'
    csv_dir = project_dir.joinpath('tempcsv')
    fin_csv = csv_dir / (filename + '.csv')

    # Setup AVF computation results Paths
    result_path = top_dir.parent / "Panalyzer_results" / filename / (filename + '_pvf.csv')
    vf_frame = pd.read_csv(result_path)
    print(vf_frame)
    time = vf_frame.iloc[:, 0]
    vf = vf_frame.iloc[:, 1]

    plt.plot(time, vf)


plot("crcbaseline")
plt.show()
