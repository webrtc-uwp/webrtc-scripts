
NO_ERROR, \
ERROR_SYSTEM_ERROR, \
ERROR_SYSTEM_MISSING_GIT, \
ERROR_SYSTEM_MISSING_PERL = range(4)

#TODO: give more details about perl it is really required
#TODO: check python version and show error if it is 3.0 or later
error_codes = {
  ERROR_SYSTEM_ERROR : "Unknown system erorr",
  ERROR_SYSTEM_MISSING_GIT : "Git is missing",
  ERROR_SYSTEM_MISSING_PERL : "Perl is missing"
}