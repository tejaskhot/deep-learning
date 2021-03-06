"""ConvNet MNIST teset"""

import numpy as np;

import theano;
import theano.tensor as T;

import telaugesa.datasets as ds;
from telaugesa.fflayers import ReLULayer;
from telaugesa.fflayers import SoftmaxLayer;
from telaugesa.convnet import ReLUConvLayer;
from telaugesa.convnet import MaxPooling;
from telaugesa.convnet import Flattener;
from telaugesa.model import FeedForward;
from telaugesa.optimize import gd_updates;
from telaugesa.cost import categorical_cross_entropy_cost;
from telaugesa.cost import L2_regularization;

n_epochs=100;
batch_size=100;

datasets=ds.load_mnist("../data/mnist.pkl.gz");
train_set_x, train_set_y = datasets[0];
valid_set_x, valid_set_y = datasets[1];
test_set_x, test_set_y = datasets[2];

n_train_batches=train_set_x.get_value(borrow=True).shape[0]/batch_size;
n_valid_batches=valid_set_x.get_value(borrow=True).shape[0]/batch_size;
n_test_batches=test_set_x.get_value(borrow=True).shape[0]/batch_size;

print "[MESSAGE] The data is loaded"

X=T.matrix("data");
y=T.ivector("label");
idx=T.lscalar();

images=X.reshape((batch_size, 1, 28, 28))

layer_0=ReLUConvLayer(filter_size=(7,7),
                      num_filters=50,
                      num_channels=1,
                      fm_size=(28,28),
                      batch_size=batch_size);
                      
pool_0=MaxPooling(pool_size=(2,2));
                      
layer_1=ReLUConvLayer(filter_size=(4,4),
                      num_filters=20,
                      num_channels=50,
                      fm_size=(11,11),
                      batch_size=batch_size);

pool_1=MaxPooling(pool_size=(2,2));

flattener=Flattener();

layer_2=ReLULayer(in_dim=320,
                  out_dim=200);
                  
layer_3=SoftmaxLayer(in_dim=200,
                     out_dim=10);
                     
model=FeedForward(layers=[layer_0, pool_0, layer_1, pool_1, flattener, layer_2, layer_3]);

out=model.fprop(images);
cost=categorical_cross_entropy_cost(out[-1], y)+L2_regularization(model.params, 0.01);
updates=gd_updates(cost=cost, params=model.params);

train=theano.function(inputs=[idx],
                      outputs=cost,
                      updates=updates,
                      givens={X: train_set_x[idx * batch_size: (idx + 1) * batch_size],
                              y: train_set_y[idx * batch_size: (idx + 1) * batch_size]});

test=theano.function(inputs=[idx],
                     outputs=model.layers[-1].error(out[-1], y),
                     givens={X: test_set_x[idx * batch_size: (idx + 1) * batch_size],
                             y: test_set_y[idx * batch_size: (idx + 1) * batch_size]});
                              
print "[MESSAGE] The model is built"

test_record=np.zeros((n_epochs, 1));
epoch = 0;
while (epoch < n_epochs):
    epoch+=1;
    for minibatch_index in xrange(n_train_batches):
        mlp_minibatch_avg_cost = train(minibatch_index);
        
        iteration = (epoch - 1) * n_train_batches + minibatch_index;
        
        if (iteration + 1) % n_train_batches == 0:
            print 'MLP MODEL';
            test_losses = [test(i) for i in xrange(n_test_batches)];
            test_record[epoch-1] = np.mean(test_losses);
            
            print(('     epoch %i, minibatch %i/%i, test error %f %%') %
                  (epoch, minibatch_index + 1, n_train_batches, test_record[epoch-1] * 100.));