"""ConvNet Layer

ConvNet base layer and extended layer

"""

import numpy as np;

import theano;
from theano.tensor.signal import downsample;
from theano.tensor.nnet import conv;

import nnet.util as util;
import nnet.nnfuns as nnfuns;

class ConvNetBase(object):
    """ConvNet base layer"""
    
    def __init__(self,
                 filter_size,
                 num_filters,
                 num_channels,
                 fm_size=None,
                 batch_size=None,
                 step=(1,1),
                 border_mode="full",
                 use_bias=True,
                 **kwargs):
        """Initialize ConvNet structure
        
        Parameters
        ----------
        filter_size : tuple
            height and width of the filter (height, width)
        num_filters : int
            number of filters
        num_channels : int
            number of channels
        fm_size : tuple
            feature map size (height, width)
        batch_size : int 
            number of example in one batch
        step : tuple
            The step (or stride) with which to slide the filters over the
            image. Defaults to (1, 1).
        border_mode : string
            valid or full convolution : "valid", "full"
        use_bias : bool
            either if use bias
        """
        
        super(ConvNetBase, self).__init__(**kwargs);
         
        self.filter_size=filter_size;
        self.num_filters=num_filters;
        self.num_channels=num_channels;
        self.fm_size=fm_size;
        self.batch_size=batch_size;
        self.step=step;
        self.border_mode=border_mode;
        self.use_bias=use_bias;
        
        self.initialize();
        
    def initialize(self, weight_type="none"):
        """Initialize weights and bias
        
        Parameters
        ----------
        weight_type : string
            type of weights: "none", "tanh", "sigmoid"
        """
        
        # should have better implementation for convnet weights
        
        fan_in = self.num_channels*np.prod(self.filter_size);
        fan_out = self.num_filters*np.prod(self.filter_size);
        
        filter_bound=np.sqrt(6./(fan_in + fan_out));
        filter_shape=(self.num_filters, self.num_channels)+(self.filter_size);
        self.filters = theano.shared(np.asarray(np.random.uniform(low=-filter_bound,
                                                                  high=filter_bound,
                                                                  size=filter_shape),
                                                dtype='float32'),
                                     borrow=True);
        
        if self.use_bias==True:
            self.bias=util.init_weights("bias", self.num_filters, weight_type=weight_type);
        
    def apply_lin(self, X):
        """Apply convoution operation
        
        Parameters
        ----------
        X : 4D tensor
            data with shape (batch_size, num_channels, height, width)
            
        Returns
        -------
        
        """
        
        Y=conv.conv2d(input=X,
                      filters=self.filters,
                      image_shape=(self.batch_size, self.num_channels)+(self.fm_size),
                      filter_shape=(self.num_filters, self.num_channels)+(self.filter_size),
                      border_mode=self.border_mode,
                      subsample=self.step);
                      
        if self.use_bias:
            Y+=self.bias.dimshuffle('x', 0, 'x', 'x');
        
        return Y;
    
    @property    
    def params(self):
        return (self.filters, self.bias);
    
    @params.setter
    def params(self, param_list):
        self.filters.set_value(param_list[0].get_value());
        self.bias.set_value(param_list[1].get_value());
        
####################################
# ConvNet Layer
####################################

class IdentityConvLayer(ConvNetBase):
    """Identity ConvNet Layer"""
    
    def __init__(self, *args, **kwargs):
        super(IdentityConvLayer, self).__init__(**kwargs);
        
    def apply(self, X):
        return self.apply_lin(X);
    
class TanhConvLayer(ConvNetBase):
    """Tanh ConvNet Layer"""
    
    def __init__(self, *args, **kwargs):
        super(TanhConvLayer, self).__init__(**kwargs);
        
    def apply(self, X):
        return nnfuns.tanh(self.apply_lin(X));
    
class SigmoidConvLayer(ConvNetBase):
    """Sigmoid ConvNet Layer"""
    
    def __init__(self, *args, **kwargs):
        super(SigmoidConvLayer, self).__init__(**kwargs);
        
    def apply(self, X):
        return nnfuns.sigmoid(self.apply_lin(X));
    
class ReLUConvLayer(ConvNetBase):
    """ReLU ConvNet Layer"""
    
    def __init__(self, *args, **kwargs):
        super(ReLUConvLayer, self).__init__(**kwargs);
        
    def apply(self, X):
        return nnfuns.relu(self.apply_lin(X));
    
####################################
# Pooling Layer
####################################

class MaxPooling(object):
    """ Max Pooling Layer """
    
    def __init__(self,
                 pool_size,
                 step=None,
                 **kwargs):
        """Initialize max pooling
        
        Parameters
        ----------
        pool_size : tuple
            height and width of pooling region
        step : tuple
            The vertical and horizontal shift (stride)
        """
        self.pool_size=pool_size;
        self.step=step;
        
    def apply(self, X):
        """apply max-pooling
        
        Parameters
        ----------
        X : 4D tensor
            data with shape (batch_size, num_channels, height, width)
            
        Returns
        -------
        pooled : 4D tensor
            max pooled out result
        """
        
        return downsample.max_pool_2d(X, self.pool_size);
    
class Flattener(object):
    """Flatten feature maps"""
    
    def apply(self, X):
        """flatten feature map
        
        Parameters
        ----------
        X : 4D tensor
            data with shape (batch_size, num_channels, height, width)
            
        Returns
        -------
        flatten_result : 2D matrix
        """
        
        return X.flatten(ndim=2);