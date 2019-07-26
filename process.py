import math
import xlrd
import matplotlib.pyplot as plt
from tslearn.utils import to_time_series_dataset
from tslearn.clustering import TimeSeriesKMeans

def preprocess_data():
    users={}
    control_ids=[]

    wb = xlrd.open_workbook('D:/belfast_ulster/Residential allocations.xls')
    sheet = wb.sheet_by_index(0)
    for i in range(sheet.nrows):
        if (sheet.cell_value(i, 1)=="C"):
            control_ids.append(int(sheet.cell_value(i,0)))
    print(len(control_ids))


    for i in range(5,9):
        file_name='D:/belfast_ulster/Data/'+'GasDataWeek '+str(i)
        file=open(file_name)
        for line in file:
            tokens = [t.strip() for t in line.split(",")]
            if(tokens[0]!='"ID"'):
                id=int(tokens[0])
                if (id in control_ids):
                    day_hour=tokens[1]
                    day=int(day_hour[:-2])
                    hour=int(day_hour[3:])
                    usage=float(tokens[2])
                    if (id in users.keys()):
                        days=users[id]
                    else:
                        days={}
                    if (day in days.keys()):
                        hours=days[day]
                    else:
                        hours={}
                    if (day in days.keys()):
                        hours=days[day]
                    else:
                        hours={}
                    hours[hour]=usage
                    days[day]=hours
                    users[id]=days
        file.close()

    usages=[]
    for key_id in users.keys():
        value_id = users[key_id]
        for key_day in value_id:
            value_day = value_id[key_day]
            usage_in_day=[]
            for key_hour in value_day:
                usage_in_day.append(value_day[key_hour])
            usages.append(usage_in_day)

    X_train=to_time_series_dataset(usages)
    return [X_train, users]


def process():
    [X_train, users]=preprocess_data()
    print(X_train.shape)
    n_users=len(users.keys())
    print(n_users)
    sz = X_train.shape[1]
    seed = 0

    min_number_of_cluster=10
    max_number_of_cluster=11

    variances = []
    nc = []

    for number_of_clusters in range(min_number_of_cluster,max_number_of_cluster):
        #number_of_clusters=10
    
    # Euclidean k-means
        print("Euclidean k-means")
        km = TimeSeriesKMeans(n_clusters=number_of_clusters, verbose=False, max_iter=50, random_state=seed)
        y_pred = km.fit_predict(X_train)
        print(len(y_pred))



    # Compute total variance
        total_variance=0
        for yi in range(number_of_clusters):
            for xx in X_train[y_pred == yi]:
                variance=0
                for i in range(len(xx.ravel())):
                    variance=variance+(xx.ravel()[i] - km.cluster_centers_[yi].ravel()[i])**2
                total_variance=total_variance+math.sqrt(variance)
        print(total_variance)
        variances.append(total_variance)
        nc.append(yi)

    """

    print(variances)
    print(nc)
    plt.figure(num=1, figsize=(10, 10))
    plt.plot(nc,variances,'r-')
    plt.xlim(min_number_of_cluster,max_number_of_cluster)
    plt.ylim(min(variances), max(variances))
    fig1 = plt.gcf()
    fig1.savefig('variance_number_of_clusters.png', dpi=100)
    """



    plt.figure(num=1, figsize=(20, 20))
    for yi in range(number_of_clusters):
        plt.subplot(5, 2, yi + 1)
        for xx in X_train[y_pred == yi]:
            plt.plot(xx.ravel(), "k-", alpha=.4)
        plt.plot(km.cluster_centers_[yi].ravel(), linewidth=5.0, color='r')
        plt.xlim(0, sz)
        plt.ylim(0, 20)
        plt.title("Cluster: "+str(yi),fontsize=14)
    fig1 = plt.gcf()
    fig1.savefig('clusters.png',dpi=100)
    fig1.clear()

    #read answer for id from survey file

    header=""

    survey_file = open('D:/belfast_ulster/Smart meters Residential pre-trial survey data - Gas.csv')
    i=0
    id_survey={}
    for line in survey_file:
        line = line.rstrip('\n')
        if (i==0):
            i=1
            header=line
        else:
            tokens = [t.strip() for t in line.split(",")]
            if ((tokens[1]=="C")):
                id_survey[int(tokens[0])]=line
    print(len(id_survey.keys()))
    print(id_survey.keys())

    #generate files for clusters


    #files = [open("pre-trial survey-cluster_{}.csv".format(x), 'w') for x in range(number_of_clusters)]
    #for file in files:
    #    file.write(header)
    #print(files)
    final_file=open("final.csv", 'w')
    final_file.write(header+', cluster\n')


    i=0
    id_cluster={}
    for key_id in users.keys():
        if(key_id in id_survey.keys()):
            number_of_occurences_in_clusters=[0] * number_of_clusters
            value_id = users[key_id]
            for key_day in value_id.keys():
                number_of_occurences_in_clusters[y_pred[i]]+=1
                i += 1
            print(number_of_occurences_in_clusters)
            c=number_of_occurences_in_clusters.index(max(number_of_occurences_in_clusters))
            id_cluster[key_id]=c
            #print(key_id)
            print(c)
            #(files[c]).write(id_survey[key_id])
            final_file.write(id_survey[key_id]+', '+str(c)+'\n')


    #for file in files:
        #file.close()
    final_file.close()





    


