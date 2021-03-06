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
from sklearn import preprocessing
from matplotlib import pyplot as plt

from discriminator import Discriminator
from generator import Generator
from gan import Gan
import mnist
import params

if params.DOWNLOAD_MNIST:
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

def discriminator_train_test_set(normal_shaped_data, mnist_data, train_test_split):
    """Creates a training and test set of the same number of mnist data and
    normal shaped data.

    Args:
        normal_shaped_data (np.array): Array with elements that are normal
            shaped. (Shape=(None, 784))
        mnist_data (np.array): The mnist training set.
        train_test_split (float): If 0.1 for example, 10% of the data is used
            for testing.

    Returns:
        X_train (np.array): The training images.
        y_train (np.array): The training labels.
        X_test (np.array): The test images.
        y_test (np.array): The test labels.
    """
    X = []
    y = []

    for i in range(len(normal_shaped_data)):
        X.append(normal_shaped_data[i])
        y.append([1, 0])
        X.append(mnist_data[i])
        y.append([0, 1])

    split = int(len(X) * train_test_split)

    X_train = X[:-split]
    y_train = y[:-split]

    X_test = X[-split:]
    y_test = y[-split:]

    return np.array(X_train), np.array(y_train), np.array(X_test), np.array(y_test)

def show_digit(X, digit):
    """Visualizes one array as an image from the MNIST dataset.
    Args:
        X (np.array): The image as an array. Shape=(784,).
        digit (int): The digit shown in the image.
    """
    pixels = X.reshape((28, 28))
    plt.title(str(digit))
    plt.imshow(pixels, cmap='gray')
    plt.show()

X = get_normal_shaped_arrays(60000, (1, 784))

X_train, y_train, X_test, y_test = discriminator_train_test_set(X, X_train, params.DISCRIMINATOR_TRAIN_TEST_SPLIT)

discriminator = Discriminator(params.DISCRIMINATOR_BATCH_SIZE, params.DISCRIMINATOR_EPOCHS)
discriminator.train(X_train, y_train)
print(discriminator.eval(X_test, y_test))

generator = Generator()

gan = Gan(generator, discriminator)
gan.set_discriminator_trainability(False)
gan.show_trainable()

X = get_normal_shaped_arrays(100000, (1, 16))
y = []
for _ in range(100000):
    y.append([0, 1])

y = np.array(y)

generator = gan.train_generator(X, y)

print(generator.summary())

pred1 = generator.predict(X[0].reshape(1, 16))
pred2 = generator.predict(X[15].reshape(1, 16))
pred3 = generator.predict(X[72].reshape(1, 16))


show_digit(pred1, 8)
show_digit(pred2, 1)
show_digit(pred3, 3)
