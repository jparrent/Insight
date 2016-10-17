#!/usr/bin/python3

from gensim.models import word2vec
from sklearn.cluster import KMeans
import time

model_file_name = 'wordmodel_allmenus_sept18_size300_window10_mincount20_workers4_batchwords40_sample1em3.mod'
model = word2vec.Word2Vec.load(model_file_name)

print(model.syn0.shape)

start = time.time()  # Start time

# Set "k" (num_clusters) to be 1/5th of the vocabulary size, or an
# average of 5 words per cluster
word_vectors = model.syn0
num_clusters = int(word_vectors.shape[0] / 5)

# Initalize a k-means object and use it to extract centroids
kmeans_clustering = KMeans(n_clusters=num_clusters)
idx = kmeans_clustering.fit_predict(word_vectors)

# Get the end time and print how long the process took
end = time.time()
elapsed = end - start
print("Time taken for K Means clustering: ", elapsed, "seconds.")
