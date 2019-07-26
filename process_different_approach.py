import math
import xlrd
import itertools as it
import matplotlib.pyplot as plt
from tslearn.utils import to_time_series_dataset
from tslearn.clustering import TimeSeriesKMeans
from tslearn import preprocessing


def preprocess_data():
    users = {}
    control_ids = []
    days={}
    first_day=335


    wb = xlrd.open_workbook('D:/belfast_ulster/Residential allocations.xls')
    sheet = wb.sheet_by_index(0)
    for i in range(sheet.nrows):
        if (sheet.cell_value(i, 1) in ["C",1,2,3] ):#):["C"]
            control_ids.append(int(sheet.cell_value(i, 0)))
    print(len(control_ids))

    for i in it.chain(range(0, 3), range(5, 13)):
        file_name = 'D:/belfast_ulster/Data/' + 'GasDataWeek ' + str(i)
        file = open(file_name)
        for line in file:
            tokens = [t.strip() for t in line.split(",")]
            if (tokens[0] != '"ID"'):
                id = int(tokens[0])
                if (id in control_ids):
                    day_hour = tokens[1]
                    day = int(day_hour[:-2])
                    if((day-first_day)% 7 not in range(4,6)):
                        #print(day)
                        hour = int(day_hour[3:])
                        usage = float(tokens[2])
                        #if(usage>15):
                            #usage=15
                        if (id in users.keys()):
                            hours = users[id]
                            hours[hour]+=usage
                            (days[id]).add(day)
                        else:
                            hours={}
                            for j in range(1,49):
                                hours[j]=0
                            days[id] = {day}
                            hours[hour] += usage
                        users[id]=hours
                        #if(id==1196):
                        #print((users[id])[17])
        print(i)
        file.close()

    usages = []
    for key_id in users.keys():
        value_id = users[key_id]
        average_usage=[]
        n=len(days[key_id])
        #print(n)
        for key_hour in value_id:
            average_usage.append(value_id[key_hour]/n)
            #if ((key_id == 1196) and (key_hour==17)):
                #print(n)
                #print(value_id[key_hour]/n)
        usages.append(average_usage)

    X_train = to_time_series_dataset(usages)

    cur_min=X_train[:, :, :].min()
    cur_max = X_train[:, :, :].max()
    cur_range=cur_max-cur_min

    for i in range(X_train.shape[0]):
        for d in range(X_train.shape[2]):
            cur_min = X_train[i, :, d].min()
            cur_max = X_train[i, :, d].max()
            cur_range = cur_max - cur_min
            if (cur_range < 0.00001):
                cur_range = 1
                print("mistake!")
            X_train[i, :, d] = (X_train[i, :, d] - cur_min) * (1. - 0.) / (cur_range) + 0.


    #print(X_train)
    return [X_train, users]


def process_da():
    [X_train, users] = preprocess_data()
    print(X_train.shape)
    n_users = len(users.keys())
    print(n_users)
    sz = X_train.shape[1]
    seed = 1
    min_number_of_cluster = 10
    max_number_of_cluster = 11

    variances = []
    nc = []

    for number_of_clusters in range(min_number_of_cluster, max_number_of_cluster):
        # number_of_clusters=10

        # Euclidean k-means
        print("Euclidean k-means")
        km = TimeSeriesKMeans(metric='euclidean',n_clusters=number_of_clusters, verbose=False, max_iter=100, random_state=seed,n_init=100, tol=10e-8)
        y_pred = km.fit_predict(X_train)
        inertia = km.inertia_
        print(inertia)
        print(len(y_pred))
        '''
        # Compute total variance
        total_variance = 0
        for yi in range(number_of_clusters):
            for xx in X_train[y_pred == yi]:
                variance = 0
                for i in range(len(xx.ravel())):
                    variance = variance + (xx.ravel()[i] - km.cluster_centers_[yi].ravel()[i]) ** 2
                total_variance = total_variance + math.sqrt(variance)
        print(total_variance)
        variances.append(total_variance)
        nc.append(yi)
        '''


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
        plt.ylim(0, 1)
        plt.title("Cluster: " + str(yi), fontsize=14)
    fig1 = plt.gcf()
    fig1.savefig('clusters.png', dpi=100)
    fig1.clear()

    # read answer for id from survey file

    header = ""

    survey_file = open('D:/belfast_ulster/Smart meters Residential pre-trial survey data - Gas.csv')
    i = 0
    id_survey = {}
    for line in survey_file:
        line = line.rstrip('\n')
        if (i == 0):
            i = 1
            header = line
        else:
            tokens = [t.strip() for t in line.split(",")]
            if ((tokens[1] in ["C","1","2","3"])):
                id_survey[int(tokens[0])] = line
    print(len(id_survey.keys()))
    print(id_survey.keys())

    # generate files for clusters


    # files = [open("pre-trial survey-cluster_{}.csv".format(x), 'w') for x in range(number_of_clusters)]
    # for file in files:
    #    file.write(header)
    # print(files)
    final_file = open("final.csv", 'w')
    final_file.write(header + ', cluster\n')

    i = 0
    id_cluster = {}
    for key_id in users.keys():
        if (key_id in id_survey.keys()):
            final_file.write(id_survey[key_id] + ', ' + str(y_pred[i]) + '\n')
        i+=1

    final_file.close()