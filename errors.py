"""
  Declared error codes and error messages.
"""

NO_ERROR, \
ERROR_SYSTEM_ERROR, \
ERROR_SYSTEM_MISSING_GIT, \
ERROR_SYSTEM_MISSING_PERL,\
ERROR_SYSTEM_FAILED_USERDEF_CREATION,\
ERROR_SYSTEM_FAILED_DELETING_USERDEF,\
ERROR_TARGET_NOT_SUPPORTED,\
ERROR_PLATFORM_NOT_SUPPORTED,\
ERROR_PREPARE_OUTPUT_FOLDER_PREPARATION_FAILED,\
ERROR_PREPARE_UPDATING_DEPS_FAILED,\
ERROR_PREPARE_GN_GENERATION_FAILED,\
ERROR_NUGET_CREATION_MISSING_FILE,\
ERROR_BUILD_OUTPUT_FOLDER_NOT_EXIST,\
ERROR_BUILD_FAILED,\
ERROR_BUILD_MERGE_LIBS_FAILED,\
ERROR_SUBPROCESS_EXECUTAION_FAILED = range(16)

#TODO: give more details about perl if it is really required
#TODO: check python version and show error if it is 3.0 or later
error_codes = {
  ERROR_SYSTEM_ERROR : 'Unknown system erorr',
  ERROR_SYSTEM_MISSING_GIT : 'Git is missing!',
  ERROR_SYSTEM_MISSING_PERL : 'Perl is missing!',
  ERROR_SYSTEM_FAILED_USERDEF_CREATION : 'Failed userdef.py file cretion!',
  ERROR_SYSTEM_FAILED_DELETING_USERDEF : 'Failed deleting userdef.py file!',
  ERROR_TARGET_NOT_SUPPORTED : 'Target is not supported!',
  ERROR_PLATFORM_NOT_SUPPORTED : 'Platform is not supported!',
  ERROR_PREPARE_OUTPUT_FOLDER_PREPARATION_FAILED : 'Failed creating output folder or preparing args.gn!',
  ERROR_PREPARE_UPDATING_DEPS_FAILED : 'Failed updating target dependencies!',
  ERROR_PREPARE_GN_GENERATION_FAILED : 'Generating WebRtc projects has failed!',
  ERROR_NUGET_CREATION_MISSING_FILE : 'File missing',
  ERROR_BUILD_OUTPUT_FOLDER_NOT_EXIST : 'Output folder doesn\'t exist',
  ERROR_BUILD_FAILED : 'Build has failed',
  ERROR_BUILD_MERGE_LIBS_FAILED : 'Merging libraries has failed!',
  ERROR_SUBPROCESS_EXECUTAION_FAILED : 'Subprocess execution has failed!'
}