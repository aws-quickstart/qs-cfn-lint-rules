# Test cases

# TODO: How to test each "rule" on its own?

# 1. Required parameter for AWS::Cloudformation::Stack resource not specified (ERROR)

# 2. "Implicit" use of "Default" value for AWS::Cloudformation::Stack resource parameter by not specifying a value for it (WARNING)

# 3. Parameter specified does not exist in template of AWS::Cloudformation::Stack resource (ERROR)

# 4. Parameter of same name in template not being passed to child which has the same name (ERROR)
# (check string Parameter Name in the value of the parameter with the same names value - Covers hard coded QSS3BucketName)

# 6. TemplateURL parsing
# 6.1 !Sub
# 6.2 TODO: Template and child template in same local path
# 6.3 TODO: If:: {}
# 6.4 TODO: Other funcs

# 6.5 Other complex forms which may be possible to calculate at run time of the test.
