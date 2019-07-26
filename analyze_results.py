import numpy as np
import pandas as pd


def analyze():
    final_results = pd.read_csv("final.csv")
    my_tab = pd.crosstab(index=final_results[" cluster"],columns="count")
    print(my_tab)

    questions_file=open('questions_to_analysis.txt')
    questions=[]

    for line in questions_file:
        questions.append(line)


    #questions=list(final_results.columns.values)
    writer = pd.ExcelWriter('analysis.xlsx', engine='xlsxwriter')

    #for question in questions[3:-1]:
    i=0
    for question in questions:
        cluster_question = pd.crosstab(index=final_results[" cluster"], columns=final_results[question[:-1]])
        name=question.split(':')[0]+"_"+str(i)
        cluster_question.to_excel(writer, sheet_name=name)
        i+=1
    writer.save()
