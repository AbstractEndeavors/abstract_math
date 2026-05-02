from abstract_utilities import *
def make_plural(string,target):
    string = string.replace(f'{target}s',target)
    return string.replace(target,f'{target}s')
def replace_units_to_plural(string):
    string = make_plural(string,'input_time_unit')
    string = make_plural(string,'input_dist_unit')
    string = make_plural(string,'output_time_unit')
    return make_plural(string,'output_dist_unit')
abs_dir = get_caller_dir()
abs_dir = os.path.join('tests')
dirs,files = get_files_and_dirs(abs_dir,allowed_exts=['.py'])
for file in files:
    try:
        contents = read_from_file(file)
        contents = replace_units_to_plural(contents)
        write_to_file(contents = contents,file_path=file)
    except Exception as e:
        print(f"could not read or convet file {file}: {e}")
