# pyFmask

## What is pyFmask

`pyFmask` is a user-friendly python CLI for Fmask 4.3 software (GERS Lab,
UCONN; https://github.com/GERSL/Fmask).

Fmask ([Zhu et al., 2015](https://doi.org/10.1016/j.rse.2014.12.014);
[Qiu et al., 2017](https://doi.org/10.1016/j.rse.2017.07.002)) is used for
automated cloud, cloud shadow, snow, and water masking for Landsats 4-8 and
Sentinel-2 images.

## Requirements

You will need Python 3.8 and Fmask 4.3 to run `pyFmask`. You can have multiple
Python versions (2.x and 3.x) installed on the same system without any problems.

## Installation

`pyFmask` can be installed directly from GitHub:

```shell
$ python -m pip install git+https://github.com/acoque/pyFmask.git@main
```

## Usage

You can use `pyFmask` through its CLI:

```shell
$ pyFmask process <image_path>
```