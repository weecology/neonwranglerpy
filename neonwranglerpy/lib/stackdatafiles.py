import os.path
import neonwranglerpy.lib.tools as tl
import neonwranglerpy.lib.utils as ut


def stackDataFilesParallel(folder_path, dst, dpID):
    """ Stack the files"""

    if not os.path.exists(folder_path):
        print(f"{folder_path} does not exists")
        return None

    filenames = tl.get_all_files(folder_path)
    filepaths = tl.get_all_files(folder_path, dir_name=True)
    variables_list = [s for s in filepaths if "variables.20" in s]
    validation_list = [s for s in filepaths if "validation" in s]
    codes_list = [s for s in filepaths if "categoricalCodes" in s]
    # copy varibles and validation files to /stackedfiles using the most recent publication date
    if variables_list:
        # get most recent variable file
        varpath = ut.get_recent_publications(variables_list)
        # get variables from the files
        variables = ut.get_variables(varpath)

    stackedpath = os.path.join(dst, 'stackedFiles')
    if not os.path.exists(stackedpath):
        print('creating stackedFiles directory')
        os.makedirs(stackedpath)

    if validation_list:
        valpath = ut.get_recent_publications(validation_list)
        validation_dst = os.path.join(stackedpath, f"validation_{dpID}.csv")
        tl.copy_zip(valpath, validation_dst)
        print("copying the most recent publication of validation file to /stackedFiles")

    if codes_list:
        codepath = ut.get_recent_publications(codes_list)
        code_dst = os.path.join(stackedpath, f"categoricalCodes_{dpID}.csv")
        tl.copy_zip(codepath, code_dst)
        print(
            "copying the most recent publication of categoricalCodes file to /stackedFiles"
        )

    # stacking the files
