import glob
import os
import sys
from lxml import etree
import pudb

class BvecBvalContainer:
    def __init__(self, dti_directory):


        self._name_to_dti_vals = dict()
        self._xml_file_root = ""
        self._generate_bvec_and_bval(dti_directory)

    def _generate_bvec_and_bval(self, dti_directory):
        """
        Generates a file name -> (bval, bvec) map, and stores file root
        @param dti_directory (string) - path to the DTI directory containing nii files
                                        and xml files
        """ 
        if not os.path.isdir(dti_directory):
            print "'{}' is not a valid directory!".format(dti_directory)
            sys.exit(1)

        xml_files = []
        name_to_dti_vals = {}
        for root, dirs, files in os.walk(dti_directory):
            for file in files:
                if file.endswith('.xml'):
                    xml_files.append(os.path.join(root, file))

        self._xml_file_root = root

        for file in xml_files:
            # stop xml parser from complaining about missing tags
            parser = etree.XMLParser(recover=True)
            root = etree.parse(file, parser)

            for dti_info in root.iter('diffusion'):
                bval = dti_info.get('bvalue')
                bvec = [dti_info.get('xgradient'),
                        dti_info.get('ygradient'),
                        dti_info.get('zgradient')]
            name, extension = os.path.splitext(file)
            nii_name = name +  '.nii'
            self._name_to_dti_vals[nii_name] = self.BPair(bval, bvec)

    def get_bval_bvec_pair(self, nii_name):
        return self._name_to_dti_vals.get(nii_name, None)

    def get_xml_file_location(self):
        return self._xml_file_root

    def write_bvals_bvecs(self, bval_path, bvec_path):

        b_pairs = self._name_to_dti_vals.values()
        bvals = [b_pair.val for b_pair in b_pairs]
        bvecs = [b_pair.vec for b_pair in b_pairs]

        bval_string = " ".join(bvals)

        with open(bval_path, 'w') as bval_file:
            bval_file.write(bval_string)

        coord_strings = []
        for i in range(3):
            coord_val = [b[i] for b in bvecs]
            coord_str = " ".join(coord_val) + "\n"
            coord_strings.append(coord_str)

        with open(bvec_path, 'w') as bvec_file:
            bvec_file.writelines(coord_strings)

    def get_b0_file_names(self):
        b0_list = []

        for name, pair in self._name_to_dti_vals.iteritems():
            if pair.is_b0():
                b0_list.append(name)

        return b0_list

    def get_dwi_file_names(self):
        dwi_list = []
        for name, pair in self._name_to_dti_vals.iteritems():
            if not pair.is_b0():
                dwi_list.append(name)
                
        return dwi_list


    class BPair:

        def __init__(self, val, vec):
            self.val = val
            self.vec = vec
        def int_value(self):
            return int(self.val)

        def float_vec(self):
            return [float(elem) for elem in vec]
        def is_b0(self):
            return self.val == '0'