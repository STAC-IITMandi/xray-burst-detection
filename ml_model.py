import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np
data = pd.read_csv('csv_file (3).csv')
d1 = data.copy()
#d2 = d1.drop(['Peak_Widths', 'Peak_Start', 'Peak_Stop'])
d2 = d1.drop(['Peak_Widths', 'Info', 'Peak_Start', 'Peak_Stop'], axis=1)
d2['Peaks'] = np.log(d2['Peaks'])
for columns in d2.columns:
    d2[columns] = (d2[columns] - min(d2[columns]))/(max(d2[columns]) - min(d2[columns]))
    
train, test = train_test_split(d2, test_size=0.3)
x1=d2
from sklearn.cluster import KMeans

# kmean=KMeans(n_clusters=3)
# kmean.fit(x1)
wcss = []
for i in range(1,20):  
    kmeans = KMeans(n_clusters=i,init='k-means++',max_iter=300,n_init=10,random_state=0)
    kmeans.fit(x1)
    wcss.append(kmeans.inertia_)
    print('Cluster', i, 'Inertia', kmeans.inertia_)
plt.plot(range(1,20),wcss)
plt.title('The Elbow Curve')
plt.xlabel('Number of clusters')
plt.ylabel('WCSS') ##WCSS stands for total within-cluster sum of square
plt.show()

kmeans = KMeans(n_clusters=6,init='k-means++',max_iter=300,n_init=10,random_state=0)
kmeans.fit(x1)
wcss.append(kmeans.inertia_)
print('Cluster', i, 'Inertia', kmeans.inertia_)
    
print(kmeans.labels_)
print(kmeans.cluster_centers_)
print(kmeans.predict(x1))
# label=[]
# for index,point in x1.iterrows():
#     min_dist_label = 0
#     for i in range(len(kmean.cluster_centers_)):
#         print(i, np.linalg.norm(np.array(point) - kmean.cluster_centers_[i]))
#         min_dist_label = i if (np.linalg.norm(np.array(point) - kmean.cluster_centers_[i]) < min_dist_label) else min_dist_label
#     label.append(min_dist_label)
    
    

