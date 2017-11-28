import click
import os
import subprocess
import logging
import sys

# LOCAL MODULES
import pipe.operations as pipe_ops

stages_dict = ['dicom_to_nii', 
'b0_registration',
'dwi_to_b0',
'skull_stripping_b0_t2',
'freesurfer_t1_to_t2', 
't2_to_fiducial_b0',
'syn_registration_of_b0_to_t2',
'create_matrix']

@click.command()
@click.option('--stage-file', type = click.Path(exists = True), 
    default = None, help = 'Specifies the stages to run, must be one of the following stages: {}'.format(stages_dict))
@click.option('--base-dir', type = click.Path(exists = True), 
    required = True, help = 'Directory containing DTI cases')
@click.option('--filename', type = click.Path(exists = True),
    required = True, help = 'Name of file containing the cases.')

def pipeline(stage_file, base_dir, filename):
    global stages_dict
    
    if stage_file is not None:
        with open(stage_file) as f:
            stages_list = [line.rstrip() for line in f]
            for stage in stages_list:
                if stage not in stages_to_run:
                    print "Stage '{}' is invalid!".format(stage)
                    sys.exit(1)

            stages_to_run = stages_list

    with open(filename) as f:
        case_list = [line.rstrip() for line in f]

        for case in case_list:
            # Setting up necessary directories
            case_dir = os.path.join(base_dir,case)
            dti_dir_name = pipe_ops.search_for_sub_dir_name(case_dir, 'dti')

            out_dir = os.path.join(case_dir, 'out')
            pipe_ops.make_dir_safe(out_dir)

            # Create bvec and bval container from xml files
            bvec_bval_cont = pipe_ops.get_bvec_bval_container(dti_dir_name)

            # Create original bvec and bval files
            bval_path = os.path.join(out_dir, 'orig.bval')
            bvec_path = os.path.join(out_dir, 'orig.bvec')
            bvec_bval_cont.write_bvals_bvecs(bval_path, bvec_path)


            super_b0_path = pipe_ops.perform_b0_registration(bvec_bval_cont.get_b0_file_names(), out_dir, False)

            registered_dwi_files = pipe_ops.register_dwi_files_to_super_b0(bvec_bval_cont.get_dwi_file_names(), super_b0_path, out_dir, False)

            skull_stripped_files = pipe_ops.skull_strip_dwi_files(registered_dwi_files, out_dir, False)

if __name__ == '__main__':
    pipeline()