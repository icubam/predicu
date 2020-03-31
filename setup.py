import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="predicu",
  version="0.0.1",
  author="Valentin Iovene",
  author_email="tgy@inria.fr",
  description="Shared data wrangling and analysis code for the "
  "PredICU-COVID-19 effort team",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/tgy/predicu",
  packages=setuptools.find_packages(),
)
