import click
import os
import subprocess
import logging
import sys
import pipe.operations as pipe_ops
import nipype.interfaces.fsl as fsl

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
            case_dir = os.path.join(base_dir,case)

            dti_dir_name = search_for_sub_dir_name(case_dir, 'dti')
            out_dir = os.path.join(case_dir, 'out')

            bvec_bval_cont = get_bvec_bval_container(case_dir, dti_dir_name, out_dir)
            b0_registration(bvec_bval_cont.get_b0_file_names(), out_dir)



def get_bvec_bval_container(case_dir, dti_directory, out_dir):

    bvec_bval_cont = pipe_ops.BvecBvalContainer(dti_directory)
    root_dir = bvec_bval_cont.get_xml_file_location()
    pipe_ops.make_dir_safe(out_dir)

    bval_path = os.path.join(out_dir, 'orig.bval')
    bvec_path = os.path.join(out_dir, 'orig.bvec')

    bvec_bval_cont.write_bvals_bvecs(bval_path, bvec_path)

    return bvec_bval_cont

def b0_registration(b0_files, out_dir):
    """ 
    """
    registered_dir = os.path.join(out_dir, 'registered_b0')
    pipe_ops.make_dir_safe(registered_dir)

    base_b0 = b0_files[0]

    flirt = fsl.FLIRT()
    flirt.inputs.reference = base_b0
    flirt.inputs.cost = 'leastsq'
    flirt.inputs.dof = 12
    flirt.inputs.verbose = 1

    flirt_out_files  = []

    for i, b0_file in enumerate(b0_files[1:]):
        flirt.inputs.in_file = b0_file
        flirt.inputs.out_file = os.path.join(registered_dir, "flirt-0{}.nii".format(i + 2))
        flirt.inputs.output_type = 'NIFTI'
        flirt_out_files.append(flirt.inputs.out_file)

        flirt.inputs.out_matrix_file = os.path.join(registered_dir, "flirt-0{}.txt".format(i + 2))
        # flirt.cmdline
        #flirt.run()

    maths = fsl.MultiImageMaths()
    maths.inputs.in_file = base_b0
    maths.inputs.op_string = "-add %s -add %s -add %s -add %s -div 5"
    maths.inputs.operand_files = flirt_out_files
    maths.inputs.output_type = 'NIFTI'
    b0_super = os.path.join(registered_dir, 'bse.nii')
    maths.inputs.out_file = b0_super

    #maths.run()

      






def search_for_sub_dir_name(starting_dir, str):
    search_str = str.lower()
    for root, dirs, files, in os.walk(starting_dir):
        for dir_name in dirs:
            if search_str in dir_name.lower():
                return os.path.join(root, dir_name)
    return None

if __name__ == '__main__':
    pipeline()