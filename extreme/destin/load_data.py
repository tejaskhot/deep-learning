#  -*- coding: utf-8 -*-
from numpy import *
import cPickle as pickle
from random import randrange
import numpy as np
#cifar_dir = '/home/habtegebrial/Desktop/python-destin/cifar-10-batches-py/'
# cifar_dir = '/home/eskender/Destin/cifar-10-batches-py/'
#  Contains loading cifar batches and
#  feeding input to lower layer nodes

#####################################################
## combining the individual pickle files
#####################################################


cifar_dir="/home/ubuntu/destin/cifar-10-batches-py/"

def load_train(num):
    data_train=pickle.load(open(cifar_dir+"train-"+str(num)+"-"+str(num+25)+".p", "rb"))
    return data_train

def load_test(num):
    data_test=pickle.load(open(cifar_dir+"test-"+str(num)+"-"+str(num+25)+".p", "rb"))
    return data_test

def load_test_full():
    test_names=np.arange(0,76,25)
    data_test=np.asarray([])
    for num in test_names:
        temp=pickle.load(open(cifar_dir+"test-"+str(num)+"-"+str(num+25)+".p", "rb"))
        if not data_test.size:
            data_test=temp
        else:
            data_test=np.vstack((data_test, temp))
        print "Testin Data Stacked till batch: ", str(num+25)
    try:
        pickle.dump(data_test, open(cifar_dir+"data_test.p","wb"))
        print "Pickled test data"
    except:
        print "Could not pickle test data"
    print "Testing data completed. Shape is: ", data_test.shape # (10000, 33800)
    return data_test

def load_train_full():
    train_names=np.arange(0,476,25)
    data_train=np.asarray([])
    for num in train_names:
        temp=pickle.load(open(cifar_dir+"train-"+str(num)+"-"+str(num+25)+".p", "rb"))
        if not data_train.size:
            data_train=temp
        else:
            data_train=np.vstack((data_train, temp))
        print "Training data Stacked till batch: ", str(num+25)
    try:
        pickle.dump(data_train, open(cifar_dir+"data_train.p","wb"))
        print "Pickled train data"
    except:
        print " Could not pickle train data"
    print "Training data completed. Shape is: ", data_train.shape   # (50000, 33800)
    return data_train

def read_cifar_file(fn):
    fo = open(fn, 'rb')
    dict = pickle.load(fo)
    fo.close()
    return dict


def load_cifar(psz=4):
    #  file strings
    filenames = ['data_batch_1', 'data_batch_2',
                 'data_batch_3', 'data_batch_4',
                 'data_batch_5', 'test_batch']

    #  gather data
    train_data = empty((50000, 3072))
    test_data = empty((10000, 3072))
    train_labels = empty(50000)
    test_labels = empty(10000)

    start = 0
    width = 10000
    for file in filenames:
        dic = read_cifar_file(cifar_dir + file)
        if start < 50000:
            train_data[start:start + width, :] = dic['data']
            train_labels[start:start + width] = array(dic['labels'])
        else:
            test_data[:, :] = dic['data']
            test_labels[:] = array(dic['labels'])

        start += width

    #  reshape data into images

    for x in range(50000):
        image = train_data[x]
        image.shape = (3, 32, 32)
        image2 = copy(image.transpose((1, 2, 0)))
        image2 = reshape(image2, (1, 3072))
        train_data[x] = image2

    for x in range(10000):
        image = test_data[x]
        image.shape = (3, 32, 32)
        image2 = copy(image.transpose((1, 2, 0)))
        image2 = reshape(image2, (1, 3072))
        test_data[x] = image2

    #  set dims
    train_data.shape = (50000, 32, 32, 3)
    test_data.shape = (10000, 32, 32, 3)

    #  get random patches
    patches = empty((200000, psz * psz * 3))
    # psz = 4
    for i in range(200000):
        im = randrange(50000)
        a = randrange(32 - psz)
        b = randrange(32 - psz)
        patch = reshape(
            train_data[im, a:a + psz, b:b + psz, :], (1, psz * psz * 3))
        patches[i] = patch

    #  get statistics
    patch_mean = mean(patches, axis=0)
    patch_std = std(patches, axis=0)

    #  zero mean and unit variance
    patches = patches - patch_mean
    patches = patches / patch_std

    #  whitening stuff using notation from:
    #  http://web.eecs.utk.edu/~itamar/Papers/ICMLA2012_Derek.pdf
    eps = 1e-9
    patch_cov = cov(patches, rowvar=0)
    d, e = linalg.eig(patch_cov)
    d = diag(d) + eps
    v = e.dot(linalg.inv(sqrt(d))).dot(e.T)
    patches = patches.dot(v)

    ret = {}
    # ret['train_data'] = train_data
    # ret['test_data'] = test_data
    # ret['train_labels'] = train_labels
    # ret['test_labels'] = test_labels
    ret['patch_mean'] = patch_mean
    ret['patch_std'] = patch_std
    ret['whiten_mat'] = v

    return ret


def loadCifar(batchNum):
    #  For training_batches specify numbers 1 to 5
    #  for the test set pass 6
    if batchNum <= 5:
        file_name = cifar_dir + '/data_batch_' + str(batchNum)
        file_id = open(file_name, 'rb')
        dict = pickle.load(file_id)
        file_id.close()
        return dict['data'], dict['labels']
    elif batchNum == 6:
        file_name = cifar_dir + '/test_batch'
        file_id = open(file_name, 'rb')
        dict = pickle.load(file_id)
        file_id.close()
        return dict['data'], dict['labels']
    else:  # here we will get the whole 50,000x3072 dataset
        I = 0
        file_name = cifar_dir + '/data_batch_' + str(I + 1)
        file_id = open(file_name, 'rb')
        dict = pickle.load(file_id)
        file_id.close()
        data = dict['data']
        labels = dict['labels']
        for I in range(1, 5):
            file_name = cifar_dir + '/data_batch_' + str(I + 1)
            file_id = open(file_name, 'rb')
            dict = pickle.load(file_id)
            file_id.close()
            data = np.concatenate((data, dict['data']), axis=0)
            labels = np.concatenate((labels, dict['labels']), axis=0)
        return data, labels


def return_node_input(input_, Position, Ratio, mode, image_type):
    if mode == 'Adjacent':  # Non overlapping or Adjacent Patches
        PatchWidth = Ratio
        PatchHeight = Ratio
        if image_type == 'Color':
            PatchDepth = 3
        else:
            PatchDepth = 1
        Patch = input_[Position[0]:Position[0] + PatchWidth, Position[1]:Position[1] + PatchHeight].reshape(1,PatchWidth * PatchWidth * PatchDepth)
    else:  # TODO Overlapping Patch could be fed to a node
        print('Overlapping Patches Are Not Implemented Yet')
        patch = np.array([0])
    return Patch
