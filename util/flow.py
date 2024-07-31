"""
Contains functions related to flow (e.g., bit, dataframe generation; seed resets).
"""

import os
import requests
from tabulate import tabulate
import numpy as np
import pandas as pd
import random
import subprocess, signal, ctypes

random.seed(114514)

def gen_result_table(axis1, axis2, matrix, info=''):
    header = [info] + [str(width) for width in axis2]
    # Create a table with the matrix data
    table = []
    for i, row in enumerate(matrix):
        table.append([axis1[i]] + list(row))

    # Print the table using tabulate
    return tabulate(table, headers=header, tablefmt='rounded_grid')


def gen_result_df(axis1, axis2, matrix, info=''):
    # use pandas to generate csv
    header = [info] + [str(width) for width in axis2]
    # Create a table with the matrix data
    table = []
    for i, row in enumerate(matrix):
        table.append([axis1[i]] + list(row))
    df = pd.DataFrame(table, columns=header)
    return df


def check_and_fill_defaults(kwargs: dict, required_fields: list, default_fields: dict):
    '''
    check if settings are valid
    and fill in default values, return the settings
    '''
    filled_kwargs = kwargs.copy()
    for field in required_fields:
        if field not in kwargs:
            raise RuntimeError(f'{field} not specified')
    for field in default_fields:
        if field not in kwargs:
            filled_kwargs[field] = default_fields[field]
    return filled_kwargs

def gen_dict_file_name(dic):
    name = ''
    for key in dic:
        name += f'{key}.{dic[key]}-'
    return name[:-1]


def gen_dict_title(dic, length_per_line=30):
    title = ''
    # produce a string in this format: key=value, key=value, ... but each line has at most length_per_line characters
    for key in dic:
        title += f'{key}={dic[key]}, '
        # if len(title) > length_per_line:
        #     title += '\n'
    return title[:-2]


def reset_seed(n=114514):
    random.seed(n)
    np.random.seed(n)


def generate_specific_array(length, data_width, value):
    params = np.zeros((length), dtype=int)
    for i in range(length):
        params[i] = value[i]

    # create array string in verilog format
    arr_str = '\'{'
    for i in range(length):
        arr_str += f'{data_width}\'d{int(params[i])}'
        if i != length-1:
            arr_str += ', '
    arr_str += '}'

    return arr_str


def generate_random_array(length, data_width, sparsity):
    params = np.zeros((length), dtype=int)
    threshold = int(length * sparsity)
    count = 0
    for i in range(length):
        count += 1
        if count > threshold:
            params[i] = random.randint(1, pow(2, data_width)-1)
    np.random.shuffle(params)

    return generate_specific_array(length, data_width, params)


def generate_specific_matrix(row_num, column_num, data_width, value):
    params = np.zeros((row_num, column_num), dtype=int)
    for i in range(row_num):
        for j in range(column_num):
            params[i][j] = value[i][j]

    # create array string in verilog format
    arr_str = '\'{'
    for i in range(row_num):
        arr_str += '\'{'
        for j in range(column_num):
            arr_str += f'{data_width}\'d{int(params[i][j])}'
            if j != column_num-1:
                arr_str += ', '
        arr_str += '}'
        if i != row_num-1:
            arr_str += ', '
    arr_str += '}'

    return arr_str


def generate_random_matrix(row_num, column_num, data_width, sparsity):
    total_num = row_num * column_num
    params = np.zeros((total_num), dtype=int)
    threshold = int(total_num * sparsity)
    count = 0
    for i in range(total_num):
        count += 1
        if count > threshold:
            params[i] = random.randint(1, pow(2, data_width)-1)
    np.random.shuffle(params)
    params = params.reshape((row_num, column_num))

    return generate_specific_matrix(row_num, column_num, data_width, params)

    # # create array string in verilog format
    # arr_str = '\'{'
    # for i in range(row_num):
    #     arr_str += '\'{'
    #     for j in range(column_num):
    #         arr_str += f'{data_width}\'d{int(params[i][j])}'
    #         if j != column_num-1:
    #             arr_str += ', '
    #     arr_str += '}'
    #     if i != row_num-1:
    #         arr_str += ', '
    # arr_str += '}'

    # return arr_str


def generate_random_matrix_3d(depth, row_num, column_num, data_width, sparsity):
    total_num = row_num * column_num * depth
    params = np.zeros((total_num), dtype=int)
    threshold = int(total_num * sparsity)
    count = 0
    for i in range(total_num):
        count += 1
        if count > threshold:
            params[i] = random.randint(1, pow(2, data_width)-1)
    np.random.shuffle(params)
    params = params.reshape((depth, row_num, column_num))

    # create array string in verilog format
    arr_str = '\'{'
    for i in range(depth):
        arr_str += '\'{'
        for j in range(row_num):
            arr_str += '\'{'
            for k in range(column_num):
                arr_str += f'{data_width}\'d{int(params[i][j][k])}'
                if k != column_num-1:
                    arr_str += ', '
            arr_str += '}'
            if j != row_num-1:
                arr_str += ', '
        arr_str += '}'
        if i != depth-1:
            arr_str += ', '
    arr_str += '}'

    return arr_str


def generate_random_matrix_4d(filter_num, depth, row_num, column_num, data_width, sparsity):
    total_num = row_num * column_num * depth * filter_num
    params = np.zeros((total_num), dtype=int)
    threshold = int(total_num * sparsity)
    count = 0
    for i in range(total_num):
        count += 1
        if count > threshold:
            params[i] = random.randint(1, pow(2, data_width)-1)
    np.random.shuffle(params)
    params = params.reshape((filter_num, depth, row_num, column_num))

    # create array string in verilog format
    arr_str = '\'{'
    for i in range(filter_num):
        arr_str += '\'{'
        for j in range(depth):
            arr_str += '\'{'
            for k in range(row_num):
                arr_str += '\'{'
                for l in range(column_num):
                    arr_str += f'{data_width}\'d{int(params[i][j][k][l])}'
                    if l != column_num-1:
                        arr_str += ', '
                arr_str += '}'
                if k != row_num-1:
                    arr_str += ', '
            arr_str += '}'
            if j != depth-1:
                arr_str += ',\n    '
        arr_str += '}'
        if i != filter_num-1:
            arr_str += ',\n  '
    arr_str += '}'

    return arr_str


def generate_flattened_bit(data_width, total_num, sparsity, number=None):
    '''
    this method will return a bit string of length total_number * data_width, for example
    if data_width = 8, and total_number is 4, then it will return 32'hdeadbeef

    currently only support data width of 4,8
    '''

    params = np.zeros((total_num), dtype=int)
    threshold = int(total_num * sparsity)
    count = 0
    for i in range(total_num):
        count += 1
        if count > threshold:
            params[i] = np.random.randint(1, pow(2, data_width)-1)

    np.random.shuffle(params)
    # print count of non zero elements
    total_bit_length = total_num * data_width
    result = str(total_bit_length) + "'h"
    for n in params:
        if data_width == 4:
            result += format(n, 'x')
        elif data_width == 8:
            result += format(n, 'x').zfill(2)
        else:
            raise Exception("unsupported data width")

    return result


def gen_long_constant_bits(length, sparsity, length_placeholder, bits_name='constfil'):
    # divide the long contstant string into multiple small one so parser will work, maximum bits per const is 8192. (the actual limit of parmys is 16384)
    assert length % 4 == 0, "length must be multiple of 4"
    num_complete = length // 8192
    num_remain = length % 8192
    str_temp = 'localparam bit [{total_length}:0] const_fil_part_{i} = {arr_str};'
    constructed_parts_consts = ''
    data_width = 4
    for i in range(num_complete):
        arr_str = generate_flattened_bit(data_width, 8192 // data_width, sparsity)
        constructed_parts_consts += str_temp.format(total_length=8191, i=i, arr_str=arr_str) + '\n'
    if num_remain != 0:
        arr_str = generate_flattened_bit(data_width, num_remain // data_width, sparsity)
        constructed_parts_consts += str_temp.format(total_length=num_remain-1, i=num_complete, arr_str=arr_str) + '\n'

    idxs = '{' + ','.join([f'const_fil_part_{i}' for i in range(num_complete + 1)]) + '}'
    constant_bits = constructed_parts_consts + f'localparam bit [{length_placeholder}-1:0] {bits_name} = {idxs};'
    return constant_bits


def bark(content='default flow notification', title='FPGA FLOW'):
    urls = os.getenv('BARKURL')
    if urls:
        urls = urls.strip().split()
        for url in urls:
            # print(url)
            if url.endswith('/'):
                url = url[:-1]

            try:
                resp = requests.get(url + f'/{title}/{content}')
                if resp.status_code == 200:
                    continue
                else:
                    print('Bark internet failed')

            except Exception as e:
                print(e)
                print('Bark unknown failed')

    else:
        print('Bark URL not set')
        return False

def start_dependent_process(cmd, **kwargs) -> subprocess.Popen:
    """
    Starts a subprocess that will terminate with the parent.
    All keyword arguments will be passed to subprocess.Popen(), except preexec_fn, which will be overwritten.
    """
    if 'preexec_fn' in kwargs:
        del kwargs['preexec_fn']
    
    def set_pdeathsig(sig = signal.SIGTERM):
        def callable():
            return ctypes.CDLL("libc.so.6").prctl(1, sig)
        return callable
    
    return subprocess.Popen(cmd, preexec_fn=set_pdeathsig(), **kwargs)