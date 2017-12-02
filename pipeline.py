import click
import os
import subprocess
import logging
import sys

# LOCAL MODULES
import pipe.operations as pipe_ops

logger = logging.getLogger('pipeline')
logger.setLevel(logging.INFO)


@click.command()
@click.option('--base-dir', type = click.Path(exists = True), 
    required = True, help = 'Directory containing DTI cases')
@click.option('--caselist', type = click.Path(exists = True),
    required = True, help = 'Name of file containing the cases.')
@click.option('--force-overwrite/--no-force-overwrite', default = False,
    help = "Overwrite existing files during all stages if on")

def pipeline(base_dir, caselist, force_overwrite):



    with open(caselist) as f:
        case_list = [line.rstrip() for line in f]

        for case in case_list:
            logger.info("Processing case '{}'".format(case))

            # Setting up necessary directories
            case_dir = os.path.join(base_dir,case)
            dti_dir_name = pipe_ops.search_for_sub_dir_name(case_dir, 'dti')

            logger.debug("Procesing directory '{}'".format(dti_dir_name))

            out_dir = os.path.join(case_dir, 'out')

            logger.debug("Creating output directory '{}'".format(out_dir))

            pipe_ops.make_dir_safe(out_dir)

            logger.info("Populating Bvec and Bval from xml files")
            # Create bvec and bval container from xml files
            bvec_bval_cont = pipe_ops.get_bvec_bval_container(dti_dir_name)

            # Create original bvec and bval files
            bval_path = os.path.join(out_dir, 'orig.bval')
            bvec_path = os.path.join(out_dir, 'orig.bvec')

            logger.debug("Writing Bvec and Bval files")

            bvec_bval_cont.write_bvals_bvecs(bval_path, bvec_path)

            logger.info("Performing b0 registration")

            super_b0_path = pipe_ops.perform_b0_registration(bvec_bval_cont.get_b0_file_names(), out_dir, force_overwrite)

            logger.info("Registering dwi files to super b0 file")

            registered_dwi_files = pipe_ops.register_dwi_files_to_super_b0(bvec_bval_cont.get_dwi_file_names(), super_b0_path, out_dir, force_overwrite)

            logger.info("Skull stripping dwi files")

            skull_stripped_files = pipe_ops.skull_strip_dwi_files(registered_dwi_files, out_dir, force_overwrite)

if __name__ == '__main__':
    pipeline()