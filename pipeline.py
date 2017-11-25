import click
import os
import subprocess
import logging
import sys

stages_to_run = ['dicom_to_nii', 
'b0_registration',
'dwi_to_b0',
'skull_stripping_b0_t2',
'freesurfer_t1_to_t2', 
't2_to_fiducial_b0',
'syn_registration_of_b0_to_t2',
'create_matrix']

@click.command()
@click.option('--stage-file', type = click.Path(exists = True), 
    default = None, help = 'Specifies the stages to run, must be one of the following stages: {}'.format(stages_to_run))
@click.option('--base-dir', type = click.Path(exists = True), 
    required = True, help = 'Directory containing DTI cases')
@click.option('--filename', type = click.Path(exists = True),
    required = True, help = 'Name of file containing the cases.')

def pipeline(stage_file, base_dir, filename):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    global stages_to_run
    
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

            env = dict(os.environ, BASEDIR=base_dir, FILENAME = filename, case = case)

            for stage in stages_to_run:

                print "Running Stage '{}' \n".format(stage)
                stage_script = os.path.join(current_dir,'pipe_functions',stage + '.sh')

                out = ""
                try:
                    out = subprocess.check_output(['sh', stage_script], env = env)
                except subprocess.CalledProcessError:
                    print "\nStage '{}' failed with non-zero return code".format(stage)
                    sys.exit(1)
                finally:
                    print out


if __name__ == '__main__':
    pipeline()