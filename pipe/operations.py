import os
import sys
import pudb
import nipype.interfaces.fsl as fsl

import pipe.structures as p_strcts

def get_bvec_bval_container(dti_directory):
    """
        Populates a BvecBvalContainer using xml files located in the dti_directory
    """

    bvec_bval_cont = p_strcts.BvecBvalContainer(dti_directory)
    root_dir = bvec_bval_cont.get_xml_file_location()


    return bvec_bval_cont

def perform_b0_registration(b0_files, out_dir, force_run = True):
    """ 
        Apply FLIRT to b0 files, and then average the result
        @params - force_run: overwrites existing registered files
        @return - super b0 path
    """
    registered_dir = os.path.join(out_dir, 'registered_b0')
    make_dir_safe(registered_dir)

    base_b0 = b0_files[0]

    flirt = fsl.FLIRT()
    flirt.inputs.reference = base_b0
    flirt.inputs.cost = 'leastsq'
    flirt.inputs.dof = 12
    flirt.inputs.verbose = 1
    flirt.inputs.output_type = 'NIFTI'

    flirt_out_files  = []

    for i, b0_file in enumerate(b0_files[1:]):
        flirt.inputs.in_file = b0_file
        flirt.inputs.out_file = os.path.join(registered_dir, "flirt-{num:02d}.nii".format(num = i + 1))
        
        flirt_out_files.append(flirt.inputs.out_file)

        flirt.inputs.out_matrix_file = os.path.join(registered_dir, "flirt-{num:02d}.txt".format(num = i + 1))

        if not os.path.isfile(flirt.inputs.out_matrix_file) or force_run:
            flirt.run()

        

    maths = fsl.MultiImageMaths()
    maths.inputs.in_file = base_b0
    maths.inputs.op_string = "-add %s -add %s -add %s -add %s -div 5"
    maths.inputs.operand_files = flirt_out_files
    maths.inputs.output_type = 'NIFTI'
    b0_super = os.path.join(registered_dir, 'bse.nii')
    maths.inputs.out_file = b0_super

    if not os.path.isfile(maths.inputs.out_file) or force_run:
        maths.run()

    return b0_super

def register_dwi_files_to_super_b0(dwi_files, super_b0 , out_dir, force_run = True):

    processed_files = []
    registered_dir = os.path.join(out_dir, 'registered_dwi_files')
    make_dir_safe(registered_dir)

    flirt = fsl.FLIRT()
    flirt.inputs.reference = super_b0
    flirt.inputs.interp = 'sinc'
    flirt.inputs.sinc_width = 7
    flirt.inputs.sinc_window = 'blackman'
    flirt.inputs.no_search = False
    flirt.inputs.verbose = 1
    flirt.inputs.padding_size = 1
    flirt.inputs.output_type = 'NIFTI'

    for i, dwi_file in enumerate(dwi_files):

        flirt.inputs.in_file = dwi_file
        flirt.inputs.out_file = os.path.join(registered_dir, "flirt-{num:02d}.nii".format(num = i+1))
        processed_files.append(flirt.inputs.out_file)
        flirt.inputs.out_matrix_file = os.path.join(registered_dir, "flirt-{num:02d}.txt".format(num = i+1))
        if not os.path.isfile(flirt.inputs.out_matrix_file) or force_run:
            flirt.run()

    return processed_files


def skull_strip_dwi_files(dwi_files, out_dir, force_run = True):

    skull_strip_dir = os.path.join(out_dir, 'maskDWI')
    make_dir_safe(skull_strip_dir)
    skull_stripped_files = []

    bet = fsl.BET()
    bet.inputs.frac = 0.30
    bet.inputs.vertical_gradient = 0.30
    bet.inputs.output_type = 'NIFTI'

    for i, dwi_file in enumerate(dwi_files):

        bet.inputs.in_file = dwi_file
        bet.inputs.out_file = os.path.join(skull_strip_dir, "flirt-{num:02d}-masked.nii".format(num = i+1))
        skull_stripped_files.append(bet.inputs.out_file)

        if not os.path.isfile(bet.inputs.out_file) or force_run:
            bet.run()

    return skull_stripped_files

def search_for_sub_dir_name(starting_dir, str):
    """
    Returns the full path to a subdirectory containing 'str'
    """

    search_str = str.lower()
    for root, dirs, files, in os.walk(starting_dir):
        for dir_name in dirs:
            if search_str in dir_name.lower():
                return os.path.join(root, dir_name)
    return None

def make_dir_safe(path):
    """
        Make a directory without any race conditions
        @return - true if newly created, false if already exists 
    """
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise
        else:
            return False
    return True
 