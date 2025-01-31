
from cluster_utils import get_rdd

from pyspark import SparkContext
from pyspark import RDD

def transform_names(string):
    #transform all the titles to lower case [a-z] without space
    string=str(string)
    string=string.lower()
    out=""
    for i in string:
        if i.isalpha():
            out= "".join([out,i])
    return out

def get_title_rdd(sc):
    rdd=get_rdd('metadata-songs',sc)
    return rdd.map(lambda x: (x[0],x[1][0][18]))

def get_hit_rdd(sc):
    return sc.pickleFile('hdfs:///user/prevel/new_pickle_hit')

def get_summer_hit_rdd(sc):
    id_title=get_title_rdd(sc)
    #id,title
    tra=id_title.map(lambda x:(transform_names(x[1]),x[0]))
    #transformed title,id
    hit_rdd=get_hit_rdd(sc)
    #rank,title(already transformed)
    hit_rdd=hit_rdd.map(lambda x:(x[1],x[0]))
    #title rank
    joined=tra.join(hit_rdd)
    #title(id,rank)
    unique=joined.groupByKey().distinct()
    unique=unique.map(lambda x:(x[1].data[0][0],x[1].data[0][1]))
    lstID=unique.collect()
    print(length(lstID))
    #to assert the matching performance (483 matches overs 540 songs)
    return unique
                    #id,rank

if __name__ == '__main__':
    sc = SparkContext()
    rdd =  get_summer_hit_rdd(sc)
    rdd.saveAsPickleFile('hdfs:///user/prevel/hits_key_rank')