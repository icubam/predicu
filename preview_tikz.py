import argparse
import os
import re
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("plot_script_path")
args = parser.parse_args()
plot_script_path = args.plot_script_path

assert os.path.isfile(plot_script_path)

subprocess.run(["python", plot_script_path])

with open(plot_script_path) as f:
    plot_script_content = f.read()

output_path = re.search(
    r'"(reports/figs/.*\.tex)"', plot_script_content
).group(1)

fig_path = os.path.basename(output_path).rsplit(".", 1)[0] + ".pdf"

subprocess.run(["cp", output_path, "/tmp"])
os.chdir("/tmp")
subprocess.run(["pdflatex", "-pdf", os.path.basename(output_path), fig_path])
subprocess.run(["open", "-a", "Skim", fig_path])
subprocess.run(
    "convert -density 300 -depth 8 -quality 85".split(" ")
    + [fig_path, fig_path.rsplit(".", 1)[0] + ".png"]
)
