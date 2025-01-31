import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from pyspark import SparkContext
import matplotlib.pyplot as pyplot

from analysis_functions import numeric_array_or_matrix_histogram, is_numeric


def print_histogram(histogram, number_of_labels=10, title="", figsize=(8, 6), dpi=80):
    n = len(histogram[1])
    sns.set(font_scale=0.75)
    fig, ax = pyplot.subplots(figsize=figsize, dpi=dpi)
    barplot = sns.barplot(range(n), histogram[1])
    barplot.set_xticks(np.arange(0, n + 1, float(n + 1) / number_of_labels))
    barplot.set_xticklabels(format_labels([
        np.interp(float(n + 1) * float(i) / float(number_of_labels), range(n + 1), histogram[0])
        for i in range(number_of_labels)
    ]))
    barplot.set_title(title)
    plt.show()


def format_labels(labels):
    return [format(i, '.2e') for i in labels]


def print_sampled_points(sampled_points, title="", x_label="", y_label="", figsize=(8, 6), dpi=80):
    _list = list(sampled_points['points'])
    _list.sort(key=lambda x: x[0])
    x = np.array([i[0] for i in _list])
    y = np.array([i[1] for i in _list])
    A = np.vstack([x, np.ones(len(x))]).T
    m, c = np.linalg.lstsq(A, y)[0]
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(111)
    ax.plot(x, y, '.')
    ax.plot(x, m * x + c, 'r', label='Fitted line')
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    plt.show()


def scatter_plot_with_song_hotness(rdd, metadata_songs_rdd, number_of_points=500):
    """
    :type rdd: RDD
    :type metadata_songs_rdd: RDD
    """
    hotness = metadata_songs_rdd.map(lambda x: (x[0], x[1]['song_hotttnesss'][0])).filter(lambda x: is_numeric(x[1]))
    joined_rdds = rdd.join(hotness)
    points = joined_rdds.sample(False, float(number_of_points)/float(joined_rdds.count())).map(lambda x: x[1]).collect()
    x = [i[0] for i in points]
    y = [i[1] for i in points]
    plt.plot(x, y, '.')
    plt.show()


def scatter_plot_with_song_hotness_and_year(rdd, metadata_songs_rdd, music_brainz_rdd, number_of_points=500):
    hotness = metadata_songs_rdd.map(lambda x: (x[0], x[1]['song_hotttnesss'][0])).filter(lambda x: is_numeric(x[1]))
    year = music_brainz_rdd.map(lambda x: (x[0], x[1]['year'][0])).filter(lambda x: not (int(x[1]) == 0))
    joined_rdds = rdd.join(hotness).join(year)
    points = joined_rdds.sample(False, float(number_of_points) / float(joined_rdds.count())).map(
        lambda x: x[1]).collect()
    x = [i[0][0] for i in points]
    y = [i[0][1] for i in points]
    z = [i[1] for i in points]
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z)
    plt.show()


def correlation_artist_hotness(sc):
    metadata_songs_rdd = sc.pickleFile(r'../data/metadata-songs')
    artist_hotness = metadata_songs_rdd.map(
        lambda x: (x[0], x[1]['song_hotttnesss'][0])
    ).filter(lambda x: is_numeric(x[1]))
    scatter_plot_with_song_hotness(artist_hotness, metadata_songs_rdd)


def correlation_tempo(sc):
    analysis = sc.pickleFile(r'../data/analysis-songs')
    metadata_songs_rdd = sc.pickleFile(r'../data/metadata-songs')
    tempo = analysis.map(lambda x: (x[0], x[1]['tempo'][0])).filter(lambda x: is_numeric(x[1]))
    scatter_plot_with_song_hotness(tempo, metadata_songs_rdd)


def correlation_tempo_and_year(sc):
    music_brainz_rdd = sc.pickleFile(r'../data/musicbrainz-songs')
    analysis_songs_rdd = sc.pickleFile(r'../data/analysis-songs')
    metadata_songs_rdd = sc.pickleFile(r'../data/metadata-songs')
    tempo = analysis_songs_rdd.map(lambda x: (x[0], x[1]['tempo'][0])).filter(lambda x: is_numeric(x[1]))
    scatter_plot_with_song_hotness_and_year(tempo, metadata_songs_rdd, music_brainz_rdd)


if __name__ == "__main__":
    sc = SparkContext(appName="Histogram")
    rdd = sc.pickleFile(r"C:\Users\marc_\Documents\Prog\ADA_Group\project\data\analysis-bars_start")
    _min, _max, histogram, number_of_filtered_elements = numeric_array_or_matrix_histogram(rdd)
    print_histogram(histogram)
    sc.stop()
