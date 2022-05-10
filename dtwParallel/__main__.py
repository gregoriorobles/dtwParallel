import argparse
import csv
import sys
import pandas as pd
from scipy.spatial import distance
import os.path
from dtw_functions import dtw, dtw_tensor_3d
from error_control import validate
import ast
import numpy as np
import configparser

class Input:
    def __init__(self):
        # config = configparser.ConfigParser()
        # print(config.read('.\dtwParallel\configuration.ini'))
        self.conf_path = '.\dtwParallel\conf.txt'
        constant_parameters = Input.read_configuration(self)
        self.errors_control = bool(constant_parameters[0])
        self.type_dtw = bool(constant_parameters[1])
        self.verbose = int(constant_parameters[2])
        self.n_threads = int(constant_parameters[3])
        #self.distance = constant_parameters[3]
        self.distance = distance.euclidean
        self.visualization = ast.literal_eval(constant_parameters[5])
        self.output_file = ast.literal_eval(constant_parameters[6])

    def read_configuration(self):
        with open(self.conf_path) as f:
            lines = f.readlines()
            f.close()
        split_lines = []
        for i in range(len(lines)):
            print(lines[i])
            split_lines.append(lines[i].split('=')[1].replace('\n', ""))
        return split_lines



def string_to_float(data):
    arr_float = []

    for i in range(len(data)):
        arr_float.append(float(data[i]))

    return arr_float


def read_data(fname):
    return pd.read_csv(fname, header=None)

def read_npy(fname):
    return np.load(fname)


def parse_args():
    print(pd.__file__)
    parser = argparse.ArgumentParser(description='Read POST run outputs.')
    parser.add_argument('file',
                        type=argparse.FileType('r'),
                        help='POST file to be analyzed.')
    return parser.parse_args()


def input_File():

    args = parse_args()
    data = read_data(args.file)
    input_obj = Input()
    if (data.shape[0] == 2) and (data.shape[0] % 2 == 0):
        MTS = False
        print("Caso univariante")
        x = string_to_float(data.iloc[0, :].values[0].split(';'))
        y = string_to_float(data.iloc[1, :].values[0].split(';'))

    elif (data.shape[0] > 3) and (data.shape[0] % 2 == 0):
        MTS = True
        x = []
        for i in range(int(data.shape[0] / 2)):
            x.append(string_to_float(data.iloc[0:int(data.shape[0] / 2), :].values[i][0].split(';')))
        y = []
        for i in range(int(data.shape[0] / 2)):
            y.append(
                string_to_float(data.iloc[int(data.shape[0] / 2):int(data.shape[0]), :].values[i][0].split(';')))

    input_obj.x = x
    input_obj.y = y

    if input_obj.errors_control:
        validate(input_obj)

    return dtw(input_obj.x, input_obj.y, input_obj.type_dtw, input_obj.distance, MTS, input_obj.visualization), input_obj.output_file


def main():
    # Input type 1: input by csv file
    if len(sys.argv) == 2:
        print("ENTRAMOS")
        # input 2D file
        if os.path.exists(sys.argv[1]) and sys.argv[1].endswith('.csv'):
            dtw_distance, output_file = input_File()
        # input 3D file
        elif os.path.exists(sys.argv[1]) and sys.argv[1].endswith('.npy'):
            args = parse_args()
            X = read_npy(args.file)
            type_dtw = "d"
            dist = distance.euclidean
            dtw_distance, output_file = dtw_tensor_3d(X, X, type_dtw, dist)
        else:
            raise ValueError('Error in load file.')
    # Input type 2: input by terminal
    elif len(sys.argv) > 2:
        print("Other input")
        # implementar para prueba sencilla
        # parser.add_argument("--x", nargs='+', type=int)
        # parser.add_argument("--y", nargs='+', type=int)
        # parser.add_argument("--dist", type=int)
        # parser.add_argument("type_dtw", type=str)
        # parser.add_argument("MTS", choices=('True','False'))
        # parser.add_argument("get_representation", choices=('True','False'))
        # args = parser.parse_args()
        # print(args.file.readlines())

    # if output_file:
    #     print("output to file")
    #     pd.DataFrame(np.array([dtw_distance])).to_csv("output.csv", index=False)
    # else:
    print(dtw_distance)


    # if args.MTS == "True":
    #     MTS = True
    # else:
    #     MTS = False
    #
    # if args.get_representation == "True":
    #     get_representation = True
    # else:
    #     get_representation = False
    #
    # print(dtw(args.x, args.y, args.type_dtw, dist, MTS, get_representation))

if __name__ == "__main__":
    main()