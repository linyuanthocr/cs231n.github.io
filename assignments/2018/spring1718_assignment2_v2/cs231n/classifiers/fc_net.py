from builtins import range
from builtins import object
import numpy as np

from cs231n.layers import *
from cs231n.layer_utils import *


class TwoLayerNet(object):
    """
    A two-layer fully-connected neural network with ReLU nonlinearity and
    softmax loss that uses a modular layer design. We assume an input dimension
    of D, a hidden dimension of H, and perform classification over C classes.

    The architecure should be affine - relu - affine - softmax.

    Note that this class does not implement gradient descent; instead, it
    will interact with a separate Solver object that is responsible for running
    optimization.

    The learnable parameters of the model are stored in the dictionary
    self.params that maps parameter names to numpy arrays.
    """

    def __init__(self, input_dim=3*32*32, hidden_dim=100, num_classes=10,
                 weight_scale=1e-3, reg=0.0):
        """
        Initialize a new network.

        Inputs:
        - input_dim: An integer giving the size of the input
        - hidden_dim: An integer giving the size of the hidden layer
        - num_classes: An integer giving the number of classes to classify
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - reg: Scalar giving L2 regularization strength.
        """
        self.params = {}
        self.reg = reg

        ############################################################################
        # TODO: Initialize the weights and biases of the two-layer net. Weights    #
        # should be initialized from a Gaussian centered at 0.0 with               #
        # standard deviation equal to weight_scale, and biases should be           #
        # initialized to zero. All weights and biases should be stored in the      #
        # dictionary self.params, with first layer weights                         #
        # and biases using the keys 'W1' and 'b1' and second layer                 #
        # weights and biases using the keys 'W2' and 'b2'.                         #
        ############################################################################
        self.params['W1'] = weight_scale*np.random.randn(input_dim,hidden_dim)
        self.params['b1'] = np.zeros(hidden_dim)
        self.params['W2'] = weight_scale*np.random.randn(hidden_dim,num_classes)
        self.params['b2'] = np.zeros(num_classes)        
        
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################


    def loss(self, X, y=None):
        """
        Compute loss and gradient for a minibatch of data.

        Inputs:
        - X: Array of input data of shape (N, d_1, ..., d_k)
        - y: Array of labels, of shape (N,). y[i] gives the label for X[i].

        Returns:
        If y is None, then run a test-time forward pass of the model and return:
        - scores: Array of shape (N, C) giving classification scores, where
          scores[i, c] is the classification score for X[i] and class c.

        If y is not None, then run a training-time forward and backward pass and
        return a tuple of:
        - loss: Scalar value giving the loss
        - grads: Dictionary with the same keys as self.params, mapping parameter
          names to gradients of the loss with respect to those parameters.
        """
        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the two-layer net, computing the    #
        # class scores for X and storing them in the scores variable.              #
        ############################################################################
        N = X.shape[0]
        hiddenout = X.reshape((N,-1)).dot(self.params['W1'])+self.params['b1'].reshape(1,-1)
        hiddenout = np.maximum(0,hiddenout)
        scores = hiddenout.dot(self.params['W2'])+self.params['b2']
        
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If y is None then we are in test mode so just return scores
        if y is None:
            return scores

        loss, grads = 0, {}
        ############################################################################
        # TODO: Implement the backward pass for the two-layer net. Store the loss  #
        # in the loss variable and gradients in the grads dictionary. Compute data #
        # loss using softmax, and make sure that grads[k] holds the gradients for  #
        # self.params[k]. Don't forget to add L2 regularization!                   #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        scores_shift = scores - np.max(scores,axis=1).reshape(-1,1)
        softmax_out = np.exp(scores_shift)/np.sum(np.exp(scores_shift),axis=1).reshape(-1,1)
        correct_scores = softmax_out[range(N),list(y)]
        loss = -np.sum(np.log(correct_scores))
        W1 = self.params['W1']
        W2 = self.params['W2']
        reg = self.reg
        loss = loss/N + 0.5*reg*(np.sum(W1*W1)+np.sum(W2*W2))
        
        dS = softmax_out.copy()
        dS[range(N),list(y)] += -1
        dS = dS/N
        grads['W2'] = (hiddenout.T).dot(dS)+reg*W2
        grads['b2'] = np.sum(dS,axis=0)
        
        dh = dS.dot(W2.T)
        drelu = (hiddenout>0)*dh
        grads['W1'] = (X.reshape(N,-1).T).dot(drelu)+reg*W1
        grads['b1'] = np.sum(drelu,axis=0)
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads


class FullyConnectedNet(object):
    """
    A fully-connected neural network with an arbitrary number of hidden layers,
    ReLU nonlinearities, and a softmax loss function. This will also implement
    dropout and batch/layer normalization as options. For a network with L layers,
    the architecture will be

    {affine - [batch/layer norm] - relu - [dropout]} x (L - 1) - affine - softmax

    where batch/layer normalization and dropout are optional, and the {...} block is
    repeated L - 1 times.

    Similar to the TwoLayerNet above, learnable parameters are stored in the
    self.params dictionary and will be learned using the Solver class.
    """

    def __init__(self, hidden_dims, input_dim=3*32*32, num_classes=10,
                 dropout=1, normalization=None, reg=0.0,
                 weight_scale=1e-2, dtype=np.float32, seed=None):
        """
        Initialize a new FullyConnectedNet.

        Inputs:
        - hidden_dims: A list of integers giving the size of each hidden layer.
        - input_dim: An integer giving the size of the input.
        - num_classes: An integer giving the number of classes to classify.
        - dropout: Scalar between 0 and 1 giving dropout strength. If dropout=1 then
          the network should not use dropout at all.
        - normalization: What type of normalization the network should use. Valid values
          are "batchnorm", "layernorm", or None for no normalization (the default).
        - reg: Scalar giving L2 regularization strength.
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - dtype: A numpy datatype object; all computations will be performed using
          this datatype. float32 is faster but less accurate, so you should use
          float64 for numeric gradient checking.
        - seed: If not None, then pass this random seed to the dropout layers. This
          will make the dropout layers deteriminstic so we can gradient check the
          model.
        """
        self.normalization = normalization
        self.use_dropout = dropout != 1
        self.reg = reg
        self.num_layers = 1 + len(hidden_dims)
        self.dtype = dtype
        self.params = {}

        ############################################################################
        # TODO: Initialize the parameters of the network, storing all values in    #
        # the self.params dictionary. Store weights and biases for the first layer #
        # in W1 and b1; for the second layer use W2 and b2, etc. Weights should be #
        # initialized from a normal distribution centered at 0 with standard       #
        # deviation equal to weight_scale. Biases should be initialized to zero.   #
        #                                                                          #
        # When using batch normalization, store scale and shift parameters for the #
        # first layer in gamma1 and beta1; for the second layer use gamma2 and     #
        # beta2, etc. Scale parameters should be initialized to ones and shift     #
        # parameters should be initialized to zeros.                               #
        ############################################################################
        L = self.num_layers
        for i in range(L):
            if i==0:
                layer_dim = (input_dim,hidden_dims[i])
            elif i<L-1:
                layer_dim = (hidden_dims[i-1],hidden_dims[i])                
            else:
                layer_dim = (hidden_dims[i-1],num_classes)
#             print("Layer %d: %d * %d"%(i,layer_dim[0],layer_dim[1]))
            self.params['W%d'%(i+1)] = weight_scale*np.random.randn(layer_dim[0],layer_dim[1])
            self.params['b%d'%(i+1)] = np.zeros(layer_dim[1])
            if self.normalization!=None and i<L-1:
                self.params['gamma%d'%(i+1)] = np.ones(layer_dim[1])
                self.params['beta%d'%(i+1)] = np.zeros(layer_dim[1])
    
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # When using dropout we need to pass a dropout_param dictionary to each
        # dropout layer so that the layer knows the dropout probability and the mode
        # (train / test). You can pass the same dropout_param to each dropout layer.
        self.dropout_param = {}
        if self.use_dropout:
            self.dropout_param = {'mode': 'train', 'p': dropout}
            if seed is not None:
                self.dropout_param['seed'] = seed

        # With batch normalization we need to keep track of running means and
        # variances, so we need to pass a special bn_param object to each batch
        # normalization layer. You should pass self.bn_params[0] to the forward pass
        # of the first batch normalization layer, self.bn_params[1] to the forward
        # pass of the second batch normalization layer, etc.
        self.bn_params = []
        if self.normalization=='batchnorm':
            self.bn_params = [{'mode': 'train'} for i in range(self.num_layers - 1)]
        if self.normalization=='layernorm':
            self.bn_params = [{} for i in range(self.num_layers - 1)]

        # Cast all parameters to the correct datatype
        for k, v in self.params.items():
            self.params[k] = v.astype(dtype)


    def loss(self, X, y=None):
        """
        Compute loss and gradient for the fully-connected net.

        Input / output: Same as TwoLayerNet above.
        """
        X = X.astype(self.dtype)
        mode = 'test' if y is None else 'train'

        # Set train/test mode for batchnorm params and dropout param since they
        # behave differently during training and testing.
        if self.use_dropout:
            self.dropout_param['mode'] = mode
        if self.normalization=='batchnorm':
            for bn_param in self.bn_params:
                bn_param['mode'] = mode
        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the fully-connected net, computing  #
        # the class scores for X and storing them in the scores variable.          #
        #                                                                          #
        # When using dropout, you'll need to pass self.dropout_param to each       #
        # dropout forward pass.                                                    #
        #                                                                          #
        # When using batch normalization, you'll need to pass self.bn_params[0] to #
        # the forward pass for the first batch normalization layer, pass           #
        # self.bn_params[1] to the forward pass for the second batch normalization #
        # layer, etc.                                                              #
        ############################################################################
        ar_cache = {}
        dp_cache = {}
        layer_input = X
        for i in range(self.num_layers-1):
            if self.normalization=='batchnorm':
                layer_input, ar_cache[i] = affine_bn_relu_forward(layer_input, self.params['W%d'%(i+1)], self.params['b%d'%(i+1)],self.params['gamma%d'%(i+1)],self.params['beta%d'%(i+1)],self.bn_params[i])
            elif self.normalization=='layernorm':
                layer_input, ar_cache[i] = affine_ln_relu_forward(layer_input, self.params['W%d'%(i+1)], self.params['b%d'%(i+1)],self.params['gamma%d'%(i+1)],self.params['beta%d'%(i+1)],self.bn_params[i])
            else:
                layer_input, ar_cache[i] = affine_relu_forward(layer_input, self.params['W%d'%(i+1)], self.params['b%d'%(i+1)])
            if self.use_dropout:
                layer_input, dp_cache[i] = dropout_forward(layer_input, self.dropout_param)
        ar_out, ar_cache[self.num_layers-1] = affine_forward(layer_input, self.params['W%d'%(self.num_layers)], self.params['b%d'%(self.num_layers)])
        
        scores = ar_out  
        
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If test mode return early
        if mode == 'test':
            return scores

        loss, grads = 0.0, {}
        ############################################################################
        # TODO: Implement the backward pass for the fully-connected net. Store the #
        # loss in the loss variable and gradients in the grads dictionary. Compute #
        # data loss using softmax, and make sure that grads[k] holds the gradients #
        # for self.params[k]. Don't forget to add L2 regularization!               #
        #                                                                          #
        # When using batch/layer normalization, you don't need to regularize the scale   #
        # and shift parameters.                                                    #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        loss, dscores = softmax_loss(ar_out,y)
        dhout = dscores
        loss = loss + 0.5*self.reg*np.sum(self.params['W%d'%(self.num_layers)] * self.params['W%d'%(self.num_layers)])
        dx, dw, db = affine_backward(dhout ,ar_cache[self.num_layers-1])
        grads['W%d'%(self.num_layers)] = dw + self.reg*self.params['W%d'%(self.num_layers)]
        grads['b%d'%(self.num_layers)] = db
        dhout = dx
        for i in range(self.num_layers-1):
            j = self.num_layers-1-i-1
            loss = loss + 0.5*self.reg*np.sum(self.params['W%d'%(j+1)]*self.params['W%d'%(j+1)])
            if self.use_dropout:
                dhout = dropout_backward(dhout, dp_cache[j])
            if self.normalization=='batchnorm':
                dx, dw, db, dgamma, dbeta = affine_bn_relu_backward(dhout,ar_cache[j])
                grads['gamma%d'%(j+1)] = dgamma
                grads['beta%d'%(j+1)] = dbeta
            elif self.normalization=='layernorm':
                dx, dw, db, dgamma, dbeta = affine_ln_relu_backward(dhout,ar_cache[j])
                grads['gamma%d'%(j+1)] = dgamma
                grads['beta%d'%(j+1)] = dbeta
            else:
                dx, dw, db = affine_relu_backward(dhout, ar_cache[j])
            grads['W%d'%(j+1)] = dw + self.reg*self.params['W%d'%(j+1)]
            grads['b%d'%(j+1)] = db    
            dhout = dx
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads
