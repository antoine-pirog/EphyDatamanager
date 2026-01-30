#! /bin/env python
#
# Michael Gibson 27 April 2015
# Modified Adrian Foy Sep 2018

def data_to_result(header, data, data_present):
    """Moves the header and data (if present) into a common object."""

    result = {}
    if header['num_amplifier_channels'] > 0 and data_present:
        result['t_amplifier'] = []

    if header['num_amplifier_channels'] > 0:
        result['spike_triggers'] = header['spike_triggers']

    result['notes'] = header['notes']
    result['frequency_parameters'] = header['frequency_parameters']

    if header['version']['major'] > 1:
        result['reference_channel'] = header['reference_channel']

    if header['num_amplifier_channels'] > 0:
        result['amplifier_channels'] = header['amplifier_channels']
        if data_present:
            result['amplifier_data'] = []

    return result
