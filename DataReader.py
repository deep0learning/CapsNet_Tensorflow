import numpy as np
import tensorflow as tf
import scipy.io as sio
from glob import glob
import os
import math
import cv2

def boundBox(img):
	minX = minY = 999
	maxX = maxY = -1

	for i in range(0,img.shape[0]):
		if img[i, :, :].max() != 0 and minY == 999:
			minY = i
		if img[:, i, :].max() != 0 and minX == 999:
			minX = i

	for i in range(img.shape[1]-1, -1, -1):
		if img[i, :, :].max() != 0 and maxY == -1:
			maxY = i
		if img[:, i:, :].max() != 0 and maxX == -1:
			maxX = i

	return minX, maxX, minY, maxY
	

def place_random(trainX):
	trainX_new = []
	for img in trainX:
		minX, maxX, minY, maxY = boundBox(img)
		minX = minY = 0
		maxX = maxY = 28

		x_len = maxX - minX
		y_len = maxY - minY

		img_new = np.zeros((40,40,1), dtype=np.float32)
		x = np.random.randint(40 - x_len , size=1)[0]
		y = np.random.randint(40 - y_len , size=1)[0]

		img_new[y:y+y_len, x:x+x_len, :] = img[minY:maxY, minX:maxX :]
		trainX_new.append(img_new)
	
	return np.array(trainX_new)

def one_hot(label, output_dim):
	one_hot = np.zeros((len(label), output_dim))
	
	for idx in range(0,len(label)):
		one_hot[idx, label[idx]] = 1
	
	return one_hot

def load_data_from_mat(path):
	data = sio.loadmat(path, struct_as_record=False, squeeze_me=True)
	for key in data:
		if isinstance(data[key], sio.matlab.mio5_params.mat_struct):
			data[key] = _todict(data[key])
	return data

def _todict(matobj):
    """
    A recursive function which constructs from matobjects nested dictionaries
    """
    dict = {}
    for strg in matobj._fieldnames:
        elem = matobj.__dict__[strg]
        if isinstance(elem, sio.matlab.mio5_params.mat_struct):
            dict[strg] = _todict(elem)
        else:
            dict[strg] = elem
    return dict

#============== Different Readers ==============

def affnist_reader(args, path):
	train_path = glob(os.path.join(path, "train/*.mat"))
	test_path = glob(os.path.join(path, "test/*.mat"))

	train_data = load_data_from_mat(train_path[0])

	trainX = train_data['affNISTdata']['image'].transpose()
	trainY = train_data['affNISTdata']['label_int']

	trainX = trainX.reshape((50000, 40, 40, 1)).astype(np.float32)
	trainY = trainY.reshape((50000)).astype(np.int32)
	trainY = one_hot(trainY, args.output_dim)

	test_data = load_data_from_mat(test_path[0])
	testX = test_data['affNISTdata']['image'].transpose()
	testY = test_data['affNISTdata']['label_int']

	testX = testX.reshape((10000, 40, 40, 1)).astype(np.float32)
	testY = testY.reshape((10000)).astype(np.int32)
	testY = one_hot(testY, args.output_dim)	

	if args.is_train:
		X = tf.convert_to_tensor(trainX, dtype=tf.float32) / 255.
		Y = tf.convert_to_tensor(trainY, dtype=tf.float32)
		data_count = len(trainX)
	else:
		X = tf.convert_to_tensor(testX, dtype=tf.float32) / 255.
		Y = tf.convert_to_tensor(testY, dtype=tf.float32)
		data_count = len(testX)

	input_queue = tf.train.slice_input_producer([X, Y],shuffle=True)
	images = tf.image.resize_images(input_queue[0] ,[args.input_width, args.input_height])
	labels = input_queue[1]

	if args.rotate:
		angle = tf.random_uniform([1], minval=-60, maxval=60, dtype=tf.float32)
		radian = angle * math.pi / 180
		images = tf.contrib.image.rotate(images, radian)

	X, Y = tf.train.batch([images, labels],
						  batch_size=args.batch_size
						  )

	return X, Y, data_count


def fashion_mnist_reader(args, path):
	#Training Data
	f = open(os.path.join(path, 'train-images-idx3-ubyte'))
	loaded = np.fromfile(file=f, dtype=np.uint8)
	trainX = loaded[16:].reshape((60000, 28, 28, 1)).astype(np.float32)

	f = open(os.path.join(path, 'train-labels-idx1-ubyte'))
	loaded = np.fromfile(file=f, dtype=np.uint8)
	trainY = loaded[8:].reshape((60000)).astype(np.int32)
	trainY = one_hot(trainY, args.output_dim)


	#Test Data
	f = open(os.path.join(path, 't10k-images-idx3-ubyte'))
	loaded = np.fromfile(file=f, dtype=np.uint8)
	testX = loaded[16:].reshape((10000, 28, 28, 1)).astype(np.float32)

	f = open(os.path.join(path, 't10k-labels-idx1-ubyte'))
	loaded = np.fromfile(file=f, dtype=np.uint8)
	testY = loaded[8:].reshape((10000)).astype(np.int32)
	testY = one_hot(testY, args.output_dim)

	if args.is_train:
		X = tf.convert_to_tensor(trainX, dtype=tf.float32) / 255.
		Y = tf.convert_to_tensor(trainY, dtype=tf.float32)
		data_count = len(trainX)
	else:
		X = tf.convert_to_tensor(testX, dtype=tf.float32) / 255.
		Y = tf.convert_to_tensor(testY, dtype=tf.float32)
		data_count = len(testX)		

	input_queue = tf.train.slice_input_producer([X, Y],shuffle=True)
	images = tf.image.resize_images(input_queue[0] ,[args.input_width, args.input_height])
	labels = input_queue[1]

	if args.rotate:
		angle = tf.random_uniform([1], minval=-60, maxval=60, dtype=tf.float32)
		radian = angle * math.pi / 180
		images = tf.contrib.image.rotate(images, radian)

	X, Y = tf.train.batch([images, labels],
						  batch_size=args.batch_size
						  )
	return X, Y, data_count


def mnist_reader(args, path):
	#Training Data
	f = open(os.path.join(path, 'train-images.idx3-ubyte'))
	loaded = np.fromfile(file=f, dtype=np.uint8)
	trainX = loaded[16:].reshape((60000, 28, 28, 1)).astype(np.float32)

	if args.random_pos:
		trainX = place_random(trainX)

	f = open(os.path.join(path, 'train-labels.idx1-ubyte'))
	loaded = np.fromfile(file=f, dtype=np.uint8)
	trainY = loaded[8:].reshape((60000)).astype(np.int32)
	trainY = one_hot(trainY, args.output_dim)


	#Test Data
	f = open(os.path.join(path, 't10k-images.idx3-ubyte'))
	loaded = np.fromfile(file=f, dtype=np.uint8)
	testX = loaded[16:].reshape((10000, 28, 28, 1)).astype(np.float32)

	f = open(os.path.join(path, 't10k-labels.idx1-ubyte'))
	loaded = np.fromfile(file=f, dtype=np.uint8)
	testY = loaded[8:].reshape((10000)).astype(np.int32)
	testY = one_hot(testY, args.output_dim)

	if args.is_train:
		X = tf.convert_to_tensor(trainX, dtype=tf.float32) / 255.
		Y = tf.convert_to_tensor(trainY, dtype=tf.float32)
		data_count = len(trainX)
	else:
		X = tf.convert_to_tensor(testX, dtype=tf.float32) / 255.
		Y = tf.convert_to_tensor(testY, dtype=tf.float32)
		data_count = len(testX)

	input_queue = tf.train.slice_input_producer([X, Y], shuffle=True)
	images = tf.image.resize_images(input_queue[0] ,[args.input_width, args.input_height])
	labels = input_queue[1]

	if args.rotate:
		angle = tf.random_uniform([1], minval=-60, maxval=60, dtype=tf.float32)
		radian = angle * math.pi / 180
		images = tf.contrib.image.rotate(images, radian)


	X, Y = tf.train.batch([images, labels],
						  batch_size=args.batch_size
						  )

	return X, Y, data_count


# currently not working
# def catsdogs_reader(args, path):
# 	def create_label_data(path, label=0):
# 		file_list = glob(path)
# 		data_count = len(file_list)

# 		one_hot = np.zeros((data_count, args.output_dim))
# 		one_hot[:,label] = 1

# 		return file_list, one_hot, data_count

# 	cats_file_paths = os.path.join(path,"*cat*")
# 	dogs_file_paths = os.path.join(path,"*dog*")

# 	cats_filename, cats_labels, cats_count = create_label_data(cats_file_paths, label=0)
# 	dogs_filename, dogs_labels, dogs_count = create_label_data(dogs_file_paths, label=1)

# 	data_count = cats_count + dogs_count

# 	all_filepaths = cats_filename + dogs_filename
# 	all_labels = np.concatenate((cats_labels, dogs_labels), 0)

# 	all_images = tf.convert_to_tensor(all_filepaths, dtype=tf.string)
# 	all_labels = tf.convert_to_tensor(all_labels, dtype=tf.float32)

# 	train_input_queue = tf.train.slice_input_producer([all_images, all_labels], shuffle=True)

# 	file_content = tf.read_file(train_input_queue[0])
# 	train_images = tf.image.decode_jpeg(file_content, channels=args.input_channel)
# 	train_labels = train_input_queue[1]

# 	#set image shape and normalize image input
# 	train_images = tf.image.resize_images(train_images,[args.input_width, args.input_height])
# 	train_images.set_shape((args.input_width, args.input_height, args.input_channel))
# 	train_images = tf.cast(train_images, tf.float32) / 255.0

# 	X, Y = tf.train.batch([train_images, train_labels],
# 						  batch_size=args.batch_size
# 						  )

# 	return X, Y, data_count



#load different datasets
def load_data(args):

	path = os.path.join(args.root_path, args.data)

	if args.data == "mnist":
		images, labels, data_count = mnist_reader(args, path)
	elif args.data == "fashion_mnist":
		images, labels, data_count = fashion_mnist_reader(args, path)
	if args.data == "affnist":
		images, labels, data_count = affnist_reader(args, path)					
	elif args.data == "catsdogs":#currently not working well using capsule_dynamic
		images, labels, data_count = catsdogs_reader(args, path)

	return images, labels, data_count 