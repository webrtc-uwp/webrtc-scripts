"""
  Declared error codes and error messages.
"""

NO_ERROR, \
ERROR_SYSTEM_ERROR, \
ERROR_SYSTEM_MISSING_GIT, \
ERROR_SYSTEM_MISSING_PERL,\
ERROR_TARGET_NOT_SUPPORTED,\
ERROR_PLATFORM_NOT_SUPPORTED,\
ERROR_PREPARE_GN_GENERATION_FAILED,\
ERROR_NUGET_CREATION_MISSING_FILE,\
ERROR_BUILD_OUTPUT_FOLDER_DEOESNT_EXIST,\
ERROR_BUILD_FAILED,\
ERROR_BUILD_MERGE_LIBS_FAILED = range(11)

ERROR_COPY_LIB_FILES_FAILED = "Failed to copy lib file!"
ERROR_UPDATE_NUSPEC_FAILED = "Failed to update .nuspec file!"
ERROR_ADD_NUSPEC_FAILED = "Failed to add lib file to .nuspec file!"

#TODO: give more details about perl if it is really required
#TODO: check python version and show error if it is 3.0 or later
error_codes = {
  ERROR_SYSTEM_ERROR : 'Unknown system erorr',
  ERROR_SYSTEM_MISSING_GIT : 'Git is missing!',
  ERROR_SYSTEM_MISSING_PERL : 'Perl is missing!',
  ERROR_TARGET_NOT_SUPPORTED : 'Target is not supported!',
  ERROR_PLATFORM_NOT_SUPPORTED : 'Platform is not supported!',
  ERROR_PREPARE_GN_GENERATION_FAILED : 'Generating WebRtc projects has failed.',
  ERROR_NUGET_CREATION_MISSING_FILE : 'File missing',
  ERROR_BUILD_OUTPUT_FOLDER_DEOESNT_EXIST : 'Output folder doesn\'t exist',
  ERROR_BUILD_FAILED : 'Build has failed',
  ERROR_BUILD_MERGE_LIBS_FAILED : 'Merging libraries has failed!'
}