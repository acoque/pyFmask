# Copyright 2021 Arthur Coqué
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The main module of pyFmask, where the CLI is defined."""

import functools
import shutil
import subprocess
import tempfile
from multiprocessing import Pool
from pathlib import Path

import click
import psutil

from pyfmask.utils import load_config, update_config, PathPath

config = load_config()


@click.group()
@click.version_option()
def cli():
    """A user-friendly python CLI for Fmask 4.x software (GERS Lab, UCONN).
    
    Fmask (Zhu et al., 2015; Qiu et al., 2017) is used for automated clouds,
    cloud shadow, snow, and water masking for Landsats 4-8 and Sentinel-2
    images.
    """


def _worker(cmd_list, path, out_dir=None, n=0):
    prefix = '' if n == 0 else f'[{n}] '
    # Extract data if needed
    if path.suffix in ('.gz', '.tar', '.tgz', '.zip'):
        tmp_dir = tempfile.TemporaryDirectory()
        click.echo(f'{prefix}extract product to {tmp_dir.name}')
        path_tmp_dir = Path(tmp_dir.name).resolve()
        shutil.unpack_archive(path, path_tmp_dir)
        if (len((lst_path := list(path_tmp_dir.glob('*'))))) == 1:
            path_tmp_dir = lst_path[0]
        if path.name[:2] == 'S2':
            path = list((path_tmp_dir / 'GRANULE').glob('L1C*/'))[0]
        else:
            path = path_tmp_dir
    else:
        if path.name[:2] == 'S2':
            path = list((path / 'GRANULE').glob('L1C*/'))[0]
    click.echo(f'{prefix}cwd: {path}')
    click.echo(prefix + 'shell cmd: ' + (cmd := ' '.join(cmd_list)))
    subprocess.run(cmd, shell=True, cwd=path)
    # Move cloud mask if asked
    if out_dir is not None:
        click.echo(f'{prefix}move cloud mask to {out_dir}')
        mask_path = list(path.glob('**/*Fmask4.tif'))[0]
        shutil.move(str(mask_path), str(out_dir))
        if mask_path.parent.name == 'FMASK_DATA':
            shutil.rmtree(str(mask_path.parent))
    # Clean up the temporary directory (if exists)
    if 'tmp_dir' in locals():
        if out_dir is None:
            click.echo((f'{prefix}no output directory has been provided: '
                        f'cloud mask will be move to {Path.home()}'))
            shutil.move(str(list(path.glob('**/*Fmask4.tif'))[0]),
                        str(Path.home()))
        tmp_dir.cleanup()


def common_options(func):
    @click.option('--cpt', type=click.FLOAT,
                  help=('cloud probability threshold for creating potential '
                        'cloud layer  [default: 10.0% for Landsats 4-7, 17.5% '
                        'for Landsat 8, and 20.0% for Sentinel-2]'))
    @click.option('--cloud', type=click.INT, default='3',
                  help='number of dilated pixels for cloud')
    @click.option('--cloud_shadow', type=click.INT, default=3,
                  help='number of dilated pixels for cloud shadow')
    @click.option('--snow', type=click.INT, default=0,
                  help='number of dilated pixels for snow')
    @click.option('--out_dir', '-o', help='')
    @click.option('--num_cpus', type=click.INT,
                  help='the maximum number of central processing units used')
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@cli.command(context_settings=dict(show_default=True))
@common_options
@click.argument('image_path', nargs=-1, required=True,
                type=PathPath(exists=True, resolve_path=True))
def process(cpt, cloud, cloud_shadow, snow, out_dir, num_cpus, image_path):
    """Apply Fmask to the input image(s)."""
    cmd_list = [config['fmask_dir'], config['mr_dir'], str(cloud),
                str(cloud_shadow), str(snow)]
    if cpt is not None:
        cmd_list.append(str(cpt))
    
    lst_cmd = [cmd_list for _ in image_path]
    lst_path = [path for path in image_path]
    lst_outdir = [out_dir for _ in image_path]
    
    cpus = [psutil.cpu_count(logical=False), len(image_path), num_cpus]
    num_cpus = min(val for val in cpus if val is not None)
    if num_cpus > 1:
        with Pool(num_cpus) as p:
            p.starmap(_worker, zip(lst_cmd, lst_path, lst_outdir,
                                   range(1, len(image_path) + 1)))
    else:
        for cmd, path, out_dir in zip(lst_cmd, lst_path, lst_outdir):
            _worker(cmd, path, out_dir)


@cli.command(context_settings=dict(show_default=True))
@common_options
@click.argument('dir_path', required=True,
                type=PathPath(exists=True, file_okay=False, resolve_path=True))
@click.pass_context
def process_fromdir(ctx, cpt, cloud, cloud_shadow, snow, out_dir, num_cpus,
                    dir_path):
    """Apply Fmask to all the images located in the given directory."""
    image_paths = tuple(dir_path.glob('*'))
    ctx.invoke(process, cpt=cpt, cloud=cloud, cloud_shadow=cloud_shadow,
               snow=snow, out_dir=out_dir, num_cpus=num_cpus,
               image_path=image_paths)


@cli.command(context_settings=dict(show_default=True))
@common_options
@click.argument('file_path', required=True,
                type=PathPath(exists=True, resolve_path=True))
@click.pass_context
def process_fromfile(ctx, cpt, cloud, cloud_shadow, snow, out_dir, num_cpus,
                     file_path):
    """Apply Fmask to the images listed in the input file."""
    with open(file_path) as f:
        image_paths = [path for p in f.readlines()
                       if (path := Path(p.strip())).exists()]
    ctx.invoke(process, cpt=cpt, cloud=cloud, cloud_shadow=cloud_shadow,
               snow=snow, out_dir=out_dir, num_cpus=num_cpus,
               image_path=image_paths)


@cli.command()
@click.argument('fmask_dir', nargs=1, required=False,
                type=click.Path(exists=True, file_okay=False, resolve_path=True))
def update_fmask_dir(fmask_dir):
    """Change the default value of FMASK_DIR.
    
    FMASK_DIR is the path to the Fmask application.
    """
    if fmask_dir is not None:
        update_config(config, 'fmask_dir', fmask_dir)
    click.echo(f'fmask_dir: {config["fmask_dir"]}')


@cli.command()
@click.argument('mr_dir', nargs=1, required=False,
                type=click.Path(exists=True, file_okay=False, resolve_path=True))
def update_mr_dir(mr_dir):
    """Change the default value of MR_DIR.
    
    MR_DIR is the path to the MATLAB Runtime (v9.6) directory.
    """
    if mr_dir is not None:
        update_config(config, 'mr_dir', mr_dir)
    click.echo(f'mr_dir: {config["mr_dir"]}')
