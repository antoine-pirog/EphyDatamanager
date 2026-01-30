#! /bin/env python
#
# Michael Gibson 23 April 2015
# Modified Adrian Foy Sep 2018

import sys, struct
import numpy as np

def read_one_data_block(data, header, indices, channel_idx, fid):
    """Reads one 60 or 128 sample data block from fid into data, at the location indicated by indices."""

    # In version 1.2, we moved from saving timestamps as unsigned
    # integers to signed integers to accommodate negative (adjusted)
    # timestamps for pretrigger data['
    is_post_V12 = bool((header['version']['major'] == 1 and header['version']['minor'] >= 2) or (header['version']['major'] > 1))
    signed_or_unsigned_int = "i" if is_post_V12 else "I"
    fmt = '<' + signed_or_unsigned_int * header['num_samples_per_data_block']
    data['t_amplifier'][indices['amplifier']:(indices['amplifier'] + header['num_samples_per_data_block'])] = np.array(struct.unpack(fmt, fid.read(4 * header['num_samples_per_data_block'])))

    if header['num_amplifier_channels'] > 0:
        tmp = np.fromfile(fid, dtype='uint16', count= header['num_samples_per_data_block'] * header['num_amplifier_channels']) # Still suboptimal I reckon, no need to read ALL data
        data['amplifier_data'][(indices['amplifier']):(indices['amplifier']+ header['num_samples_per_data_block'])] = tmp.reshape(header['num_amplifier_channels'], header['num_samples_per_data_block'])[channel_idx,:]

    if header['num_aux_input_channels'] > 0:
        fid.read(2 * int((header['num_samples_per_data_block'] / 4) * header['num_aux_input_channels']))

    if header['num_supply_voltage_channels'] > 0:
        fid.read(2 * header['num_supply_voltage_channels'])

    if header['num_temp_sensor_channels'] > 0:
        fid.read(2 * header['num_temp_sensor_channels'])

    if header['num_board_adc_channels'] > 0:
        fid.read(2 * (header['num_samples_per_data_block']) * header['num_board_adc_channels'])

    if header['num_board_dig_in_channels'] > 0:
        fid.read(2 * header['num_samples_per_data_block'])

    if header['num_board_dig_out_channels'] > 0:
        fid.read(2 * header['num_samples_per_data_block'])
