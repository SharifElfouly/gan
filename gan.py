"""
This program uses a generative adverserial neural network (gan), to create
digits that look like digits from the MNIST dataset.
Process:
    1) The discriminator is trained to distinguish a digit from the MNIST
        dataset, from a fake one, generated by a normal distribution.
    2) The generator creates digits from a normal distribution. Its output is
        given to the discriminator.
"""
import numpy as np
from sklearn.preprocessing import Normalizer

from discriminator import Discriminator
import mnist

# set to True to download and save the MNIST dataset.
DOWNLOAD_MNIST = False

if DOWNLOAD_MNIST:
    X_train, y_train, X_test, y_test = mnist.init()
else:
    X_train, y_train, X_test, y_test = mnist.load()

def get_normal_shaped_array(shape):
    """Returns a normal shaped array.

    The elements of the array follow a normal distribution and are between (0,1).

    Args:
        shape (tuple): The shape of the returned array.

    Returns:
        normal_shaped (np.array): Array with elements that are normal shaped.
    """
    normal = np.random.normal(size=shape)

    # sort from smallest to largest.
    normal = np.sort(normal, axis=0)

    min = np.amin(normal)

    # sets the smallest element to 0.
    new_normal = normal - min

    new_normal_max = np.amax(new_normal)

    # sets the largest element to 1.
    normal_shaped = new_normal / new_normal_max

    # set the first/last element wich are 0/1 to 0.0001/0.999 to make them
    # easier for an activation function like sigmoid.
    normal_shaped[0] = 1e-4
    normal_shaped[len(normal_shaped) - 1] = 0.999

    return normal_shaped

def get_normal_shaped_arrays(n_arrays, shape):
    """Returns a number of normal shaped array.

    The elements of one array follow a normal distribution and are between (0,1).

    Args:
        n_arrays (int): How many arrays.
        shape (tuple): The shape of the returned array.

    Returns:
        normal_shaped (np.array): Array with arrays that are normal shaped.
    """
    normal_shaped = []

    for _ in range(n_arrays):
        normal_shaped.append(get_normal_shaped_array(shape))

    return np.array(normal_shaped).reshape(n_arrays, shape[1])

def get_discriminator_train_set(normal_shaped_data, mnist_data):
    """Creates a training set of the same number of mnist data and normal shaped
    data.

    Args:
        normal_shaped_data (np.array): Array with elements that are normal
            shaped. (Shape=(None, 784))
        mnist_data (np.array): The mnist training set.

    Returns:
        X (np.array): The images.
        y (np.array): The labels.
    """
    X = []
    y = []

    for i in range(len(normal_shaped_data)):
        X.append(normal_shaped_data[i])
        y.append([1, 0])
        X.append(mnist_data[i])
        y.append([0, 1])

    return np.array(X), np.array(y)

X = get_normal_shaped_arrays(60000, (1, 784))

X, y = get_discriminator_train_set(X, X_train)

discriminator = Discriminator()
discriminator.train(X, y)

test_normal_shaped_arrays = get_normal_shaped_arrays(10000, (1, 784))
X, y = get_discriminator_train_set(test_normal_shaped_arrays, X_test)
evaluation = discriminator.eval(X, y)

print(evaluation)

print(discriminator.model.predict(get_normal_shaped_arrays(10, (1, 784))))

print('###############')

print(discriminator.model.predict(X_train[0:10]))
