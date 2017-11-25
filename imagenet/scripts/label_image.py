from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse

from imagenet.lib.label_image import FacesClassificator

if __name__ == "__main__":
    file_name = "imagenet/tf_files/flower_photos/daisy/3475870145_685a19116d.jpg"
    model_file = "imagenet/tf_trained/retrained_graph.pb"
    label_file = "imagenet/tf_trained/retrained_labels.txt"
    input_height = 224
    input_width = 224
    input_mean = 128
    input_std = 128
    input_layer = "input"
    output_layer = "final_result"
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", help="image to be processed")
    parser.add_argument("--graph", help="graph/model to be executed")
    parser.add_argument("--labels", help="name of file containing labels")
    parser.add_argument("--input_height", type=int, help="input height")
    parser.add_argument("--input_width", type=int, help="input width")
    parser.add_argument("--input_mean", type=int, help="input mean")
    parser.add_argument("--input_std", type=int, help="input std")
    parser.add_argument("--input_layer", help="name of input layer")
    parser.add_argument("--output_layer", help="name of output layer")
    args = parser.parse_args()
    
    if args.graph:
        model_file = args.graph
    if args.image:
        file_name = args.image
    if args.labels:
        label_file = args.labels
    if args.input_height:
        input_height = args.input_height
    if args.input_width:
        input_width = args.input_width
    if args.input_mean:
        input_mean = args.input_mean
    if args.input_std:
        input_std = args.input_std
    if args.input_layer:
        input_layer = args.input_layer
    if args.output_layer:
        output_layer = args.output_layer
    
    classificator = FacesClassificator(model_file=model_file,
                                       file_name=file_name,
                                       label_file=label_file,
                                       input_height=input_height,
                                       input_width=input_width,
                                       input_mean=input_mean,
                                       input_std=input_std,
                                       input_layer=input_layer,
                                       output_layer=output_layer)
    
    classes = classificator.get_probabilities(file_name, debug=True)
    
    for name, prob in sorted(classes.items()):
        print(f'{name}: {prob}')
