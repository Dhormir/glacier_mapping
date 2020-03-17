import io
import threading
import numpy as np

def serialize(array):
    with io.BytesIO() as f:
        np.save(f, array)
        return f.getvalue()

def deserialize(data):
    with io.BytesIO(data) as f:
        return np.load(f)

class AtomicCounter:
    ''' From https://gist.github.com/benhoyt/8c8a8d62debe8e5aa5340373f9c509c7 '''
    def __init__(self, initial=0):
        """Initialize a new atomic counter to given initial value (default 0)."""
        self.value = initial
        self._lock = threading.Lock()

    def increment(self, num=1):
        """Atomically increment the counter by num (default 1) and return the
        new value.
        """
        with self._lock:
            self.value += num
            return self.value



def to_categorical(y, num_classes=None):
    """Converts a class vector (integers) to binary class matrix.
    E.g. for use with categorical_crossentropy.
    # Arguments
        y: class vector to be converted into a matrix
            (integers from 0 to num_classes).
        num_classes: total number of classes.
    # Returns
        A binary matrix representation of the input. The classes axis
        is placed last.
    """
    y = np.array(y, dtype='int')
    input_shape = y.shape
    if input_shape and input_shape[-1] == 1 and len(input_shape) > 1:
        input_shape = tuple(input_shape[:-1])
    y = y.ravel()
    if not num_classes:
        num_classes = np.max(y) + 1
    n = y.shape[0]
    categorical = np.zeros((n, num_classes), dtype=np.float32)
    categorical[np.arange(n), y] = 1
    output_shape = input_shape + (num_classes,)
    categorical = np.reshape(categorical, output_shape)
    return categorical


def to_one_hot(im, class_num):
    one_hot = np.zeros((class_num, im.shape[-2], im.shape[-1]), dtype=np.float32)
    for class_id in range(class_num):
        one_hot[class_id, :, :] = (im == class_id).astype(np.float32)
    return one_hot

def to_one_hot_batch(batch, class_num):
    one_hot = np.zeros((batch.shape[0], class_num, batch.shape[-2], batch.shape[-1]), dtype=np.float32)
    for class_id in range(class_num):
        one_hot[:, class_id, :, :] = (batch == class_id).astype(np.float32)
    return one_hot

def class_prediction_to_img(y_pred, color_map=None):
    assert len(y_pred.shape) == 3, "Input must have shape (height, width, num_classes)"
    height, width, num_classes = y_pred.shape

    if color_map is None:
        color_map = np.array([
            [0,0,1],
            [0,0.5,0],
            [0.5,1,0.5],
            [0.5,0.375,0.375],
        ], dtype=np.float32)

    img = np.zeros((height, width, 3), dtype=np.float32)
    y_pred_temp = y_pred.argmax(axis=2)
    for c in range(num_classes):
        for ch in range(3):
            img[:, :, ch] += y_pred_temp[:, :, c] * color_map[c, ch]
    return img

def nlcd_to_img(img):
    return np.vectorize(NLCD_COLOR_MAP.__getitem__, signature='()->(n)')(img).astype(np.uint8)

def get_shape_layer_by_name(shapes, layer_name):
    for layer in shapes:
        if layer["name"] == layer_name:
            return layer
    return None

def get_random_string(length):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    return "".join([alphabet[np.random.randint(0, len(alphabet))] for i in range(length)])
