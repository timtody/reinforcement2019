#!/usr/bin/python3

'''This module holds the definitions of all network models.'''

from tensorflow.keras.layers import Input, Dense, Conv2D, MaxPooling2D, Flatten, Reshape
from tensorflow.keras.models import Model
from tensorflow.keras import optimizers
def definePacmanTestModel1(conf):
    # Define Model
    inputShape = (conf.input_y_dim, conf.input_x_dim, conf.c_channels)

    state = Input(inputShape)                                                                                           # pre 0 in
    x = Conv2D(32, (3, 3), activation='relu', padding='same', name='Conv0')(state)                                      # conv 0
    
    x = Conv2D(8, (3, 3), activation='relu', padding='valid', name='Conv1')(x)                                          # conv 1

    x = MaxPooling2D((2,2))(x)                                                                                          # pooling

    x = Conv2D(8, (3, 3), activation='relu', padding='valid', name='Conv2')(x)                                          # conv 2

    x = MaxPooling2D((2,2))(x)                                                                                          # pooling

    x = Conv2D(8, (3, 3), activation='relu', padding='valid', name='Conv3')(x)                                          # conv 3

    x = MaxPooling2D((2,2))(x)                                                                                          # pooling

    x = Flatten()(x)                                                                                                    # flatten

    x = Dense(100, activation='relu')(x)                                                                                # fc

    x = Dense(100, activation='relu')(x)                                                                                # fc

    qsa = Dense(conf.num_actions, activation='linear')(x)                                                               # out

    # Make Model
    model = Model(state, qsa)

    # Configure Optimizer
    if conf.optimizer == 'adadelta':
        optimizer = optimizers.Adadelta(lr=conf.learning_rate, decay=0.0, rho=0.95)
    elif conf.optimizer == 'sgd':
        optimizer = optimizers.SGD(lr=conf.learning_rate)
    elif conf.optimizer == 'adam':
        optimizer = optimizers.Adam(lr=conf.learning_rate)
    elif conf.optimizer == 'adagrad':
        optimizer = optimizers.Adagrad(lr=conf.learning_rate)
    else:
        print("Optimizer '{0}' not found.".format(conf.optimizer))
        exit(0)
    
    return model, optimizer
