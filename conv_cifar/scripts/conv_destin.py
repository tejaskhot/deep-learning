"""
@author: Tejas Khot
@contact: tjskhot@gmail.com
"""
__author__='tejas'

from destin.network import *
from destin.load_data import *
import cPickle as pickle
from time import time
from sklearn import svm
import nnet.datasets as ds
import os

t_0 = time()
# *****Define Parameters for the Network and nodes

# Network Params
num_layers = 4
patch_mode = 'Adjacent'
image_type = 'Color'
network_mode = True
cifar_stat=[]
# For a Node: specify Your Algorithm Choice and Corresponding parameters

# ******************************************************************************************
#
#                           Incremental Clustering
#
num_nodes_per_layer = [[8, 8], [4, 4], [2, 2], [1, 1]]
num_cents_per_layer = [50, 25, 25 ,50]
pool_size = [(16,1),(2,2),(2,2),(1,1)]        #pooling size: The first number is the number of vector 
                                              #you want to pool. For example, (64,1) will pool all the 
                                              #vector in the first layer. (16,1) will divide the first layer 
                                              #in to 4 quarters and pool each of them. (4,1) will divide the 
                                              #first layer in to 16th pieces and pool each of them
print "Uniform DeSTIN with Clustering"
algorithm_choice = 'Clustering'
alg_params = {'mr': 0.01, 'vr': 0.01, 'sr': 0.001, 'DIMS': [],
             'CENTS': [], 'node_id': [],
             'num_cents_per_layer': num_cents_per_layer}
# ******************************************************************************************

#Load Data, 10 loads 5 batches in total 50,000
# 1 to 5 load batch_1 to batch_5training images, 1 to five
# Declare a Network Object and load Training Data

DESTIN = Network( num_layers, algorithm_choice, alg_params, num_nodes_per_layer, cifar_stat , patch_mode, image_type,)
#, , , , cifar_stat, patch_mode='Adjacent', image_type='Color'
DESTIN.setmode(network_mode)
DESTIN.set_lowest_layer(0)
# Load Data
# Modify the location of the training data in file "load_data.py"

# data = np.random.rand(5,32*32*3)
# Initialize Network; there is is also a layer-wise initialization option
DESTIN.init_network()

train_names=np.arange(0,476,25)

#Train the Network
print "DeSTIN Training/with out Feature extraction"
for epoch in range(5):
    counter=0
    for num in train_names:
        data=load_train(num)
        for I in range(data.shape[0]):  # For Every image in the data set batch
            counter+=1
            if counter % 10000 == 0:
                print("Training Iteration Image Number : %d" % counter)
            for L in range(DESTIN.number_of_layers):
                if L == 0:
                    img=data[I][:].reshape(50, 38, 38)
                    img=img.swapaxes(0,1).swapaxes(1,2) ## (38, 38, 50)
                    img=img[3:-3, 3:-3, :]  ## (32, 32, 50)
                    # This is equivalent to sharing centroids or kernels
                    DESTIN.layers[0][L].load_input(img, [4, 4])
                    DESTIN.layers[0][L].do_layer_learning()
                    #DESTIN.layers[0][L].shared_learning()
                else:
                    DESTIN.layers[0][L].load_input(DESTIN.layers[0][L - 1].nodes, [2, 2])
                    DESTIN.layers[0][L].do_layer_learning()
                    #DESTIN.layers[0][L].shared_learning()
    print "Epoch " + str(epoch+1) + " completed"
try:
    pickle.dump( DESTIN, open( "DESTIN_conv", "wb" ) )
    print "Pickled DeSTIN "
except:
    print "Could not pickle DeSTIN"    
print "done with destin training network"

del data
# DESTIN=pickle.load( open( "DESTIN_conv", "rb" ) )


print("DeSTIN running | Feature Extraction over the Training Data")
network_mode = False
DESTIN.setmode(network_mode)

# Testing it over the training set

if not os.path.exists('train'):
    os.makedirs('train')

counter=0
for num in train_names:
    data=load_train(num)
    for I in range(data.shape[0]):  # For Every image in the data set
        counter+=1
        if counter % 1000 == 0:
            print("Testing Iteration Number : Completed till Image: %d" % counter)
        for L in range(DESTIN.number_of_layers):
            if L == 0:
                img=data[I][:].reshape(50, 38, 38)
                img=img.swapaxes(0,1).swapaxes(1,2) ## (38, 38, 50)
                img=img[3:-3, 3:-3, :]  ## (32, 32, 50)
                DESTIN.layers[0][L].load_input(img, [4, 4])
                DESTIN.layers[0][L].do_layer_learning()
            else:
                DESTIN.layers[0][L].load_input(DESTIN.layers[0][L - 1].nodes, [2, 2])
                DESTIN.layers[0][L].do_layer_learning()
        DESTIN.update_belief_exporter(pool_size, True ,'average_exc_pad')             #( maxpool_shape , ignore_border, mode)
        if counter in range(199, 50999, 200):
            Name = 'train/' + str(counter) + '.txt'
            #file_id = open(Name, 'w')
            np.savetxt(Name, np.array(DESTIN.network_belief['belief']))
            #file_id.close()
            # Get rid-off accumulated training beliefs
            DESTIN.clean_belief_exporter()

print("Feature Extraction with the test set")

if not os.path.exists('test'):
    os.makedirs('test')    

test_names=np.arange(0,76,25)
counter=0

for num in test_names:
    data=load_test(num)
    for I in range(data.shape[0]):  # For Every image in the data set
        counter+=1
        if counter % 1000 == 0:
            print("Testing Iteration Number : Completed till Image: %d" % (counter+50000))
        for L in range(DESTIN.number_of_layers):
            if L == 0:
                img=data[I][:].reshape(50, 38, 38)
                img=img.swapaxes(0,1).swapaxes(1,2) ## (38, 38, 50)
                img=img[3:-3, 3:-3, :]  ## (32, 32, 50)
                DESTIN.layers[0][L].load_input(img, [4, 4])
                DESTIN.layers[0][L].do_layer_learning()  # Calculates belief for
            else:
                DESTIN.layers[0][L].load_input(DESTIN.layers[0][L - 1].nodes, [2, 2])
                DESTIN.layers[0][L].do_layer_learning()
        DESTIN.update_belief_exporter(pool_size, True ,'average_exc_pad') 
        if counter in range(199, 10199, 200):
            Name = 'test/' + str(counter) + '.txt'
            np.savetxt(Name, np.array(DESTIN.network_belief['belief']))
            # Get rid-off accumulated training beliefs
            DESTIN.clean_belief_exporter()

del data

print "Training With SVM"
print("Loading training and test labels")

trainData, trainLabel, testData, testLabel=ds.load_CIFAR10("/home/ubuntu/destin/cifar-10-batches-py")
del trainData
del testData

# Load Training and Test Data/Extracted from DeSTIN

# here we do not use the whole set of feature extracted from DeSTIN
# We use the features which are extracted from the top few layers
print("Loading training and testing features")

I = 199
Name = 'train/' + str(I + 1) + '.txt'
trainData = np.ravel(np.loadtxt(Name))


for I in range(399, 50000, 200):
    Name = 'train/' + str(I + 1) + '.txt'
    file_id = open(Name, 'r')
    Temp = np.ravel(np.loadtxt(Name))
    trainData = np.hstack((trainData, Temp))

del Temp



Len = np.shape(trainData)[0]
Size = np.size(trainData)

Width = Len/50000
print Len
print Width*50000
trainData = trainData.reshape((50000, Width))

# Training SVM
SVM = svm.LinearSVC(C=1)
# C=100, kernel='rbf')
print "Training the SVM"
trainLabel = np.squeeze(np.asarray(trainLabel).reshape(50000, 1))
#print trainData
SVM.fit(trainData, trainLabel)
print("Training Score = %f " % float(100 * SVM.score(trainData, trainLabel)))
#print("Training Accuracy = %f" % (SVM.score(trainData, trainLabel) * 100))
eff = {}
eff['train'] = SVM.score(trainData, trainLabel) * 100
del trainData


testData = np.array([])
print("Loading training and testing features")

I = 399
Name = 'test/' + str(I + 1) + '.txt'
testData = np.ravel(np.loadtxt(Name))

for I in range(599, 10000, 200):
    Name = 'test/' + str(I + 1) + '.txt'
    file_id = open(Name, 'r')
    Temp = np.ravel(np.loadtxt(Name))
    testData = np.hstack((testData, Temp))

del Temp

Len = np.shape(testData)[0]
Size = np.size(testData)


I = 399
Name = 'test/' + str(I + 1) + '.txt'
testData1 = np.ravel(np.loadtxt(Name))
print np.shape(testData1)[0]/200.0


Width = np.float(Len)/9800.0
print Len
print Size
testData = testData.reshape((9800, Width))

print "Predicting Test samples"
print("Test Score = %f" % float(100 * SVM.score(testData, testLabel[200:10000])))
#print("Training Accuracy = %f" % (SVM.score(testData, testLabel) * 100))
eff['test'] = SVM.score(testData, testLabel[200:10000]) * 100
io.savemat('accuracy.mat', eff)



print "Total time taken: ", time()-t_0



