import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from keras.layers import Input, MaxPooling1D, Dense, Dropout, Conv1D, Reshape, BatchNormalization, Flatten
from keras import regularizers
from keras.models import Model
import keras
import tensorflow as tf
import pdb
import warnings
from keras import backend as K
import DataPreprocessing
from gensim.models import FastText, KeyedVectors, Word2Vec
from keras.models import Sequential
from keras.optimizers import Adam

warnings.filterwarnings("ignore")

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
config.gpu_options.per_process_gpu_memory_fraction = 0.9
K.tensorflow_backend.set_session(tf.Session(config=config))

with tf.device("/GPU:0"):
    epochs = 10
    batch_size = 64

    datasets = pd.read_csv('./data/Morphs.csv')
    datasets = datasets.sample(frac=1)
    chat = DataPreprocessing.mainProcessing(datasets.comment)
    embedding_model = Word2Vec.load("8_2_word2vec.model")
    X = [embedding_model[i] for i in chat]

    for num in range(0, len(X)):
        X[num] = X[num].reshape(-1)
    X = np.array(X)
    Y1 = np.array(datasets.Slanglabel).reshape(-1, 1)
    Y2 = np.array(datasets.NotSlanglabel).reshape(-1, 1)
    Y = np.concatenate((Y1, Y2), axis=1)
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, train_size=0.8,test_size=0.2)
    X_train = X_train.reshape(-1, 400, 1)
    X_test = X_test.reshape(-1, 400, 1)

    adam = Adam(lr=1e-4, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.0)


    model = Sequential()
    model.add(Dense(400, input_shape=(X.shape[1], 1), activation="relu"))
    model.add(BatchNormalization())
    model.add(Conv1D(filters=400, kernel_size=5, activation='relu'))
    model.add(Conv1D(filters=400, kernel_size=3, activation='sigmoid'))
    model.add(Conv1D(filters=400, kernel_size=3, activation='sigmoid'))
    model.add(Conv1D(filters=400, kernel_size=3 , activation='sigmoid'))
    model.add(MaxPooling1D(pool_size=3))
    model.add(Dropout(0.4))
    model.add(Flatten())
    model.add(Dense(500, activation='relu'))
    model.add(Dense(250, activation='relu'))
    model.add(Dense(125, activation='relu'))
    model.add(Dense(50, activation='relu'))
    model.add(Dense(2, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer=adam, metrics=[keras.metrics.Recall(), keras.metrics.Precision(), keras.metrics.Accuracy()])
    model.summary()
    history = model.fit(X_train, Y_train, epochs=epochs, batch_size=batch_size, validation_split=0.11)

    from sklearn.metrics import recall_score, accuracy_score, f1_score, precision_score

    result_X = []
    result_Y = []

    for i in model.predict(X_test):
        if i[0] > i[1]:
            result_X.append(1)
        else:
            result_X.append(0)

    for i in Y_test:
        result_Y.append(i[0])

    print("recall: " + str(recall_score(np.array(result_Y), np.array(result_X))))
    print("precision: " + str(precision_score(np.array(result_Y), np.array(result_X))))
    print("f1_score: " + str(f1_score(np.array(result_Y), np.array(result_X))))
    print("accurancy: " + str(accuracy_score(np.array(result_Y), np.array(result_X))))