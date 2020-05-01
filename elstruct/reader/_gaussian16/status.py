""" status checkers
"""
import autoparse.pattern as app
import autoparse.find as apf
import elstruct.par


# Exit message for the program
def has_normal_exit_message(output_string):
    """ does this output string have a normal exit message?
    """
    pattern = app.escape('Normal termination of Gaussian 16')
    return apf.has_match(pattern, output_string, case=False)


# Parsers for convergence success messages
def _has_scf_convergence_message(output_string):
    """ does this output string have a convergence success message?
    """
    scf_str1 = (
        'Initial convergence to {} achieved.  Increase integral accuracy.' +
        app.LINE_FILL + app.NEWLINE + app.LINE_FILL + app.escape('SCF Done:')
    ).format(app.EXPONENTIAL_FLOAT_D)
    scf_str2 = app.escape('Rotation gradient small -- convergence achieved.')
    pattern = app.one_of_these([scf_str1, scf_str2])
    return apf.has_match(pattern, output_string, case=False)


def _has_opt_convergence_message(output_string):
    """ does this output string have a convergence success message?
    """
    pattern = (
        app.escape('Optimization completed.') +
        app.LINE_FILL + app.NEWLINE + app.LINE_FILL +
        app.escape('-- Stationary point found.')
    )
    return apf.has_match(pattern, output_string, case=False)


def _has_irc_convergence_message(output_string):
    """ does this output string have a convergence success message?
    """
    pattern = app.escape('Reaction path calculation complete.')
    return apf.has_match(pattern, output_string, case=False)


# Parsers for various error messages
def _has_scf_nonconvergence_error_message(output_string):
    """ does this output string have an SCF non-convergence message?
    """
    pattern = app.padded(app.NEWLINE).join([
        app.escape('Convergence criterion not met.'),
        app.escape('SCF Done:')
    ])
    return apf.has_match(pattern, output_string, case=False)


def _has_opt_nonconvergence_error_message(output_string):
    """ does this output string have an optimization non-convergence message?
    """
    pattern = app.padded(app.NEWLINE).join([
        app.escape('Optimization stopped.'),
        app.escape('-- Number of steps exceeded,')
    ])
    return apf.has_match(pattern, output_string, case=False)


def _has_irc_nonconvergence_error_message(output_string):
    """ does this output string have an optimization non-convergence message?
    """
    pattern = app.escape('Maximum number of corrector steps exceeded')
    return apf.has_match(pattern, output_string, case=False)


ERROR_READER_DCT = {
    elstruct.par.Error.SCF_NOCONV: _has_scf_nonconvergence_error_message,
    elstruct.par.Error.OPT_NOCONV: _has_opt_nonconvergence_error_message,
    elstruct.par.Error.IRC_NOCONV: _has_irc_nonconvergence_error_message
}
SUCCESS_READER_DCT = {
    elstruct.par.Success.SCF_CONV: _has_scf_convergence_message,
    elstruct.par.Success.OPT_CONV: _has_opt_convergence_message,
    elstruct.par.Success.IRC_CONV: _has_irc_convergence_message
}


def error_list():
    """ list of errors that be identified from the output file
    """
    return tuple(sorted(ERROR_READER_DCT.keys()))


def success_list():
    """ list of sucesss that be identified from the output file
    """
    return tuple(sorted(SUCCESS_READER_DCT.keys()))


def has_error_message(error, output_string):
    """ does this output string have an error message?
    """
    assert error in error_list()
    error_reader = ERROR_READER_DCT[error]
    return error_reader(output_string)


def check_convergence_messages(error, success, output_string):
    """ check if error messages should trigger job success or failure
    """
    assert error in error_list()
    assert success in success_list()

    job_success = False
    has_error = ERROR_READER_DCT[error](output_string)
    if has_error:
        has_success = ERROR_READER_DCT[success](output_string)
        if has_success:
            job_success = True
    else:
        job_success = True

    return job_success
