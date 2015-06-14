# -*- coding: utf-8 -*-
__author__ = 'teddy'
"""
@note: An implementation of DeSTIN Network architecture 
"""
import scipy.io as io
from load_data import *
from layer import *

# io.savemat(file_name,Dict,True)
# TODO: get ridoff the sequential requirements like first feed the layer
# an input the you can initialize it


class Network():
    """
    An implementation of DeSTIN 

    This class creates the network. 
    """

    def __init__(self, 
                 num_layers, 
                 alg_choice, 
                 alg_params, 
                 num_nodes_per_layer, 
                 cifar_stat=None, 
                 patch_mode='Adjacent', 
                 image_type='Color'):

        """
        Initialize DeSTIN

        @param num_layers: number of layers 
        @param alg_choice: choice of algorithm - one from ["Clustering", "Auto-Encoder", "LogRegresion"]
        @param alg_params: Dictionary of various parameters needed for learning algorithm 
        @param num_nodes_per_layer: number of nodes present in each layer of DeSTIN
        @param cifar_stat: parameters needed for the CIFAR dataset
        @param patch_mode: patch selection mode for images 
        @param image_type: type of images to be used
        """

        self.network_belief = {}
        self.lowest_layer = 1
        # this is going to store beliefs for every image DeSTIN sees
        self.network_belief['belief'] = np.array([])
        self.save_belief_option = 'True'
        self.belief_file_name = 'beliefs.mat'
        self.number_of_layers = num_layers
        self.algorithm_choice = alg_choice
        self.algorithm_params = alg_params
        self.number_of_nodesPerLayer = num_nodes_per_layer
        self.patch_mode = patch_mode
        self.image_type = image_type
        self.layers = [
            [Layer(j, num_nodes_per_layer[j], cifar_stat, self.patch_mode, self.image_type) for j in range(num_layers)]]

    def setmode(self, mode):
        """
        Sets the network training mode

        @param mode: True indicates that the network is training
        """
        self.operating_mode = mode
        for I in range(self.number_of_layers):
            self.layers[0][I].mode = mode

    def init_network(self):
        """
        Initialize all layers of the network
        """
        for L in range(self.number_of_layers):
            self.initLayer(L)

    def set_lowest_layer(self, lowest_layer):
        """
        Sets the indicated layer to be the lowest one

        @param lowest_layer: value of lowest network layer i.e. starting layer
        """
        self.lowest_layer = lowest_layer

    def initLayer(self, layer_num):
        """
        Initialize all layers with the learning parameters

        @param layer_num: layer number 
        """
        self.layers[0][layer_num].init_layer_learning_params(self.algorithm_choice, 
                                                            self.algorithm_params)

    def train_layer(self, layer_num):
        """
        Train all layers based on the network mode

        @param layer_num: layer number to train 
        """
        self.layers[0][layer_num].do_layer_learning(self.operating_mode)

    def update_belief_exporter(self):
        """
        Updates the belief states across the network
        """
        for i in range(self.lowest_layer, self.number_of_layers):
            for j in range(len(self.layers[0][i].nodes)):
                for k in range(len(self.layers[0][i].nodes[0])):
                    if self.network_belief['belief'] == np.array([]):
                        self.network_belief['belief'] = np.array(self.layers[0][i].nodes[j][k].belief).ravel()
                    else:
                        self.network_belief['belief'] = np.hstack((np.array(self.network_belief['belief']),
                                                                  np.array(self.layers[0][i].nodes[j][k].belief).ravel()))

    def update_belief_exporter(self, maxpool_shape , ignore_border, mode):
        input = T.dmatrix('input')
        for i in range(self.lowest_layer, self.number_of_layers):
            pool_out = downsample.max_pool_2d(input, maxpool_shape[i] , ignore_border=ignore_border, mode=mode)   
            f = theano.function([input],pool_out)    #function of pooling belief vector, maxpool_shape[i] = pool size
            temp_belief = np.array([])
            for j in range(len(self.layers[0][i].nodes)):
                for k in range(len(self.layers[0][i].nodes[0])):
                    if temp_belief == np.array([]):
                        temp_belief = np.array(self.layers[0][i].nodes[j][k].belief).ravel()
                    else:
                        temp_belief = np.hstack((np.array(temp_belief),
                                                np.array(self.layers[0][i].nodes[j][k].belief).ravel()))           
                        
            no_of_centroids = self.algorithm_params['num_cents_per_layer'][i]
            no_of_nodes = self.number_of_nodesPerLayer[i][0]**2
            temp_belief = temp_belief.reshape(no_of_nodes,no_of_centroids)

            if no_of_nodes != 4 and no_of_nodes != 1:
                temp_belief_a = temp_belief[0:no_of_nodes/2,:]                  # split the temp_belief into two parts 
                temp_belief_b = temp_belief[no_of_nodes/2:no_of_nodes,:]        
                matrix_a = np.zeros((no_of_nodes/4, no_of_centroids))           
                matrix_b = np.zeros((no_of_nodes/4, no_of_centroids))          
                temp_belief = np.array([])
                a=0 
                b=0
                a2=0 
                b2=0
                a1=0
                b1=0
                for n in range(no_of_nodes/2):
                    if no_of_nodes == 16:                              #rearrange the node order in the second layer
                        if ( n / 2 )%2 == 0 :
                            matrix_a[a,:] = temp_belief_a[n,:]
                            a=a+1
                        else: 
                            matrix_b[b,:] = temp_belief_a[n,:]
                            b=b+1

                    elif no_of_nodes == 64:                                #rearrange the node order in the first layer
                        if ( n / 4 )%2 == 0 :  # (n/4)%2
                            if ((n / 2) % 2) == 0 : 
                                matrix_a[a1,:] = temp_belief_a[n,:]
                            else:
                                matrix_a[a1+4,:] = temp_belief_a[n,:]  
                                a1=a1+1                      
                        else : 
                            if (n / 2) % 2 == 0 : 
                                matrix_b[b1,:] = temp_belief_a[n,:]
                            else:
                                matrix_b[b1+4,:] = temp_belief_b[n,:]
                                b1=b1+1

                temp_belief = np.hstack((np.array(matrix_a).ravel(),np.array(matrix_b).ravel())) 
                a=0 
                b=0

                for n in range(no_of_nodes/2):
                    if no_of_nodes ==16 :                             #rearrange the node order in the second layer
                        if ( n / 2 )%2 == 0 :
                            matrix_a[a,:] = temp_belief_b[n,:]
                            a=a+1
                        else: 
                            matrix_b[b,:] = temp_belief_b[n,:]           
                            b=b+1

                    elif no_of_nodes == 64:                    #rearrange the node order in the first layer
                        if ( n / 4 )%2 == 0 :  # (n/4)%2
                            if ((n / 2) % 2) == 0 : 
                                matrix_a[a1,:] = temp_belief_b[n,:]
                            else:
                                matrix_a[a2+4,:] = temp_belief_b[n,:]  
                                a2=a2+1                      
                    else : 
                        if (n / 2) % 2 == 0 : 
                            matrix_b[b2,:] = temp_belief_b[n,:]
                        else:
                            matrix_b[b2+4,:] = temp_belief_b[n,:]
                            b2=b2+1
 
                temp_belief = np.hstack((np.array(temp_belief),np.array(matrix_a).ravel())) 
                temp_belief = np.hstack((np.array(temp_belief),np.array(matrix_b).ravel()))
                temp_belief = temp_belief.reshape(no_of_nodes,no_of_centroids)  

            #invals = np.array(temp_belief)
            pool_temp_belief=(f(temp_belief))
            #print 'pool',pool_temp_belief
            if self.network_belief['belief'] == np.array([]):
                self.network_belief['belief'] = np.array(pool_temp_belief).ravel()
            else:
                self.network_belief['belief'] = np.hstack((np.array(self.network_belief['belief']),
                                                          np.array(pool_temp_belief).ravel()))
            #print self.network_belief['belief'].shape

    def dump_belief(self, num_of_images):
        """
        Saving belief states for all images in a file 

        @param num_of_images: number of images 
        """
        total_belief_len = len(np.array(self.network_belief).ravel())
        single_belief_len = total_belief_len / num_of_images
        print np.array(self.network_belief).ravel()
        belief = np.array(self.network_belief).reshape(num_of_images, single_belief_len)
        io.savemat(self.belief_file_name, belief)

    def clean_belief_exporter(self):
        """
        Delete all beliefs i.e. clean instantiation
        """
        self.network_belief['belief'] = np.array([])
