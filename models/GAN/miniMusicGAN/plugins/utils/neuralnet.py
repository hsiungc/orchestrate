"""
    Utilities Classes for Naural Network and Layers
"""

import numpy as np
import tensorflow as tf


# global supported layers
SUPPORTED_LAYER_TYPES = (
    'reshape', 'mean', 'sum', 'dense', 'identity', 'conv1d', 'conv2d', 'conv3d',
    'transconv2d', 'transconv3d', 'avgpool2d', 'avgpool3d', 'maxpool2d',
    'maxpool3d'
)

class Layer(object):
    """Base class for all layers"""
    def __init__(self, tensor_in, structure=None, condition=None,
                 slope_tensor=None, name=None, reuse=None):
        """
            Class Constructor
            Inputs:
                tensor_in { tf.Tensor }: input tensor
                structure { dict }: layer structure
                condition { tf.Tensor }: condition tensor
                slope_tensor { tf.Tensor }: slope tensor for leaky relu
                name { str }: layer name
                reuse { bool }: reuse flag    
        """

        if not isinstance(tensor_in, tf.Tensor):
            raise TypeError("`tensor_in` must be of tf.Tensor type")

        self.tensor_in = tensor_in

        if structure is not None:
            with tf.compat.v1.variable_scope(name, reuse=reuse) as scope:
                self.scope = scope
                if structure[0] not in SUPPORTED_LAYER_TYPES:
                    raise ValueError("Layer type {} not supported".format(structure[0]))
                self.layer_type = structure[0]
                self.tensor_out = self.build(structure, condition, slope_tensor)
                self.vars = tf.compat.v1.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES,
                                                        self.scope.name)
        else:
            self.scope = None
            self.layer_type = 'bypass'
            self.tensor_out = tensor_in
            self.vars = []

        
    def __repr__(self):
        """Return the string representation of the layer"""
        return "Layer({}, type={}, input_shape={}, output_shape={})".format(
            self.scope.name, self.layer_type, self.tensor_in.get_shape(),
            self.tensor_out.get_shape())

    
    def get_summary(self):
        """Return the summary string."""
        return "{:36} {:12} {:30}".format(
            self.scope.name, self.layer_type, str(self.tensor_out.get_shape()))


    def build(self, structure, condition, slope_tensor):
        """Build the layer based on the provided structure."""
        # Mean layers
        if self.layer_type == 'mean':
            keepdims = structure[1] if len(structure) > 1 else False
            return tf.reduce_mean(self.tensor_in, 
                                    axis=structure[1], 
                                    keepdims=keepdims, 
                                    name='mean')


        # Summation layers
        if self.layer_type == 'sum':
            keepdims = structure[2] if len(structure) > 2 else False
            return tf.reduce_sum(self.tensor_in, 
                                    axis=structure[1], 
                                    keepdims=keepdims, 
                                    name='sum')
        
        # Reshape layers
        if self.layer_type == 'reshape':
            if np.prod(structure[1]) != np.prod(self.tensor_in.get_shape()[1:]):
                raise ValueError("Bad reshape size: {} to {} at {}".format(
                    self.tensor_in.get_shape()[1:], structure[1],
                    self.scope.name))
            if isinstance(structure[1], int):
                reshape_shape = (-1, structure[1])
            else:
                reshape_shape = (-1,) + structure[1]
            return tf.reshape(self.tensor_in, reshape_shape, 'reshape')


    
        # Condition
        if condition is None:
            self.conditioned = self.tensor_in

        elif self.layer_type == 'dense':
            self.conditioned = tf.concat([self.tensor_in, condition], 1)

        elif self.layer_type in ('conv1d', 
                                'conv2d', 
                                'transconv2d', 
                                'conv3d',
                                'transconv3d'):

            if self.layer_type == 'conv1d':
                reshape_shape = (-1, 1, condition.get_shape()[1])

            elif self.layer_type in ('conv2d', 'transconv2d'):
                reshape_shape = (-1, 1, 1, condition.get_shape()[1])

            else: # ('conv3d', 'transconv3d')
                reshape_shape = (-1, 1, 1, 1, condition.get_shape()[1])

            reshaped = tf.reshape(condition, reshape_shape)
            out_shape = ([-1] + self.tensor_in.get_shape()[1:-1]
                         + [condition.get_shape()[1]])
                         
            to_concat = reshaped * tf.ones(out_shape)
            self.conditioned = tf.concat([self.tensor_in, to_concat], -1)
