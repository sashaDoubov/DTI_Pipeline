# DTI_Pipeline

This pipeline is used for preprocessing of DTI images, specifically those in the ADNI database.

The input files should be arranged in the following format:
```
base_dir/
├── case n
    ├── Axial_DTI
    ├── Axial_T2_Star
    └── Sag_IR-SPGR
```

A *caselist* file must be creating, which lists the cases located in the base directory.

Usage:  
`python pipeline.py --help` : prints out help about the tool  
`python pipeline.py --base-dir {dir} --caselist {list}` : minimal amount of arguments to run the tool  
`python pipeline.py --base-dir {dir} --caselist {list} --force-overwrite` : overwrites all existing files in each stage

