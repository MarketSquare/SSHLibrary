
def get_variables(arg) :
    if arg == 'ipv6':
        variables = {'HOST': '::1'}
    else:
        variables = {'HOST': 'localhost'}
    return variables
