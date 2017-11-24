from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time

import numpy as np
import tensorflow as tf


class FacesClassificator:
    def __init__(self, **kwargs):
        self._model_file = getattr(kwargs, 'graph', 'imagenet/tf_trained/retrained_graph.pb')
        self._label_file = getattr(kwargs, 'labels', 'imagenet/tf_trained/retrained_labels.txt')
        self._input_height = getattr(kwargs, 'input_height', 224)
        self._input_width = getattr(kwargs, 'input_width', 224)
        self._input_mean = getattr(kwargs, 'input_mean', 128)
        self._input_std = getattr(kwargs, 'input_std', 128)
        self._input_layer = getattr(kwargs, 'input_layer', 'input')
        self._output_layer = getattr(kwargs, 'output_layer', 'final_result')
        
        self._graph = self._load_graph(self._model_file)
        self._labels = self._load_labels(self._label_file)
    
    @staticmethod
    def _load_graph(model_file):
        graph = tf.Graph()
        graph_def = tf.GraphDef()
        
        with open(model_file, 'rb') as f:
            graph_def.ParseFromString(f.read())
        with graph.as_default():
            tf.import_graph_def(graph_def)
        
        return graph
    
    @staticmethod
    def _read_tensor_from_image_file(file_name, input_height=299, input_width=299,
                                     input_mean=0, input_std=255):
        input_name = 'file_reader'
        output_name = 'normalized'
        file_reader = tf.read_file(file_name, input_name)
        if file_name.endswith('.png'):
            image_reader = tf.image.decode_png(file_reader, channels=3,
                                               name='png_reader')
        elif file_name.endswith('.gif'):
            image_reader = tf.squeeze(tf.image.decode_gif(file_reader,
                                                          name='gif_reader'))
        elif file_name.endswith('.bmp'):
            image_reader = tf.image.decode_bmp(file_reader, name='bmp_reader')
        else:
            image_reader = tf.image.decode_jpeg(file_reader, channels=3,
                                                name='jpeg_reader')
        float_caster = tf.cast(image_reader, tf.float32)
        dims_expander = tf.expand_dims(float_caster, 0);
        resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
        normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
        sess = tf.Session()
        result = sess.run(normalized)
        
        return result
    
    def _load_labels(self, label_file):
        label = []
        proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
        for l in proto_as_ascii_lines:
            label.append(l.rstrip())
        return label
    
    def get_probabilities(self, file_name, debug=False):
        t = self._read_tensor_from_image_file(file_name,
                                              input_height=self._input_height,
                                              input_width=self._input_width,
                                              input_mean=self._input_mean,
                                              input_std=self._input_std)
        
        input_name = 'import/' + self._input_layer
        output_name = 'import/' + self._output_layer
        input_operation = self._graph.get_operation_by_name(input_name)
        output_operation = self._graph.get_operation_by_name(output_name)
        
        with tf.Session(graph=self._graph) as sess:
            start = time.time()
            results = sess.run(output_operation.outputs[0],
                               {input_operation.outputs[0]: t})
            end = time.time()
        results = np.squeeze(results)
        
        top_k = results.argsort()[-5:][::-1]
        
        if debug:
            print('\nEvaluation time (1-image): {:.3f}s\n'.format(end - start))
        
        return {self._labels[i]: results[i] for i in top_k}
