import json
import numpy as np
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse,HttpResponse
from .form import UserForm
import pandas as pd
from urllib.parse import unquote, quote

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyEncoder, self).default(obj)
  


@login_required
def home(request):
    return render(request, "home/index.html", {})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username = username, password = password)
        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'admin/login.html', {'error': 'Username or password is incorrect'})
    else:
        return render(request, 'admin/login.html')
    
def logout(request):
    auth_logout(request)
    return redirect('home')


def register(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        
        if form.is_valid():
            form.save() 
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')

            user = authenticate(username = username, password = password, first_name = first_name, last_name = last_name) 
            auth_login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'admin/register.html', {'form': form})
    else:
        form = UserForm()
    return render(request, 'admin/register.html', {'form': form})
@login_required
def dashboard(request):
    career_cluster = pd.read_csv("static/All_Career_Clusters.csv")
    career_category = ["Agriculture, Food & Natural Resources","Transportation, Distribution & Logistics","Architecture & Construction","Science, Technology, Engineering & Mathematics","Health Science","Business Management & Administration","Hospitality & Tourism","Education & Training","Human Services","Finance","Information Technology","Government & Public Administration","Law, Public Safety, Corrections & Security","Manufacturing","Marketing"]
    career_category.sort()
    
    all_job = json.dumps(career_cluster['Occupation'].tolist())
    return render(request, 'admin/dashboard.html', {"career_category": list(career_category),"all_job":all_job})

@login_required
def overall(request):
    career_cluster = pd.read_csv("static/All_Career_Clusters.csv")
    career_category = ["Agriculture, Food & Natural Resources","Transportation, Distribution & Logistics","Architecture & Construction","Science, Technology, Engineering & Mathematics","Health Science","Business Management & Administration","Hospitality & Tourism","Education & Training","Human Services","Finance","Information Technology","Government & Public Administration","Law, Public Safety, Corrections & Security","Manufacturing","Marketing"]
    career_category.sort()
    job_patents_timeseries = pd.read_csv("static/job_patents_timeseries_newprepro_fbfore.csv",index_col=0)
    job_trend = pd.read_csv("static/job_patent_trend_newprepro.csv",index_col=0)
    max_list = {}
    
    for col in job_trend.columns:
        if col in job_patents_timeseries.columns:
            job_trend_list = job_trend[col].tolist()
            max_list.update({col: job_trend_list})



    sorted_dict = dict(sorted(max_list.items(), key=lambda x: x[1][4], reverse=True))
    predicted_job_1 = {k: sorted_dict[k] for k in list(sorted_dict)[:6]}
    predicted_job = dict(sorted(predicted_job_1.items(), key=lambda x: x[1][1], reverse=True))
    trend = []
    for i in predicted_job.values():
        trend.append({'trend_value': i[0], 'change': i[1:]})
    myList_data = {}
    for i in predicted_job.keys():
        myList_data.update({i: job_patents_timeseries[i].tolist()})
    myList_data_4 = []
    for i,j in predicted_job.items():
        types = 0
        if j[0] == 0:
            types = 0
        elif j[0] == 1:
            types = 1
        elif j[0] == -1:
            types = -1

        myList_data_4.append({'name': i, 'trend_value': types, 'change': round(j[1:][0],1)})
    myList_data_1 = []
    for i,j in myList_data.items():
        myList_data_1.append({'name': i, 'data': j})
    all_job = json.dumps(career_cluster['Occupation'].tolist())
    return render(request, 'admin/default.html', {"myList_data": myList_data_1,"trend":myList_data_4,"career_category": list(career_category),"all_job":all_job})

@login_required
def details(request):
    data = request.GET.get('param')
    career_category = ["Agriculture, Food & Natural Resources","Transportation, Distribution & Logistics","Architecture & Construction","Science, Technology, Engineering & Mathematics","Health Science","Business Management & Administration","Hospitality & Tourism","Education & Training","Human Services","Finance","Information Technology","Government & Public Administration","Law, Public Safety, Corrections & Security","Manufacturing","Marketing"]
    job = unquote(data)
    job = job.replace("amp;", "")
    job_trend = pd.read_csv("static/job_patent_trend_newprepro.csv")
    trend_value = job_trend[job].tolist()[0]
    change = job_trend[job].tolist()[1]
    job_details = pd.read_csv("static/job_details.csv")
    job_patents_timeseries = pd.read_csv("static/job_patents_timeseries_newprepro_fbfore.csv")
    single_graph = job_patents_timeseries[job].tolist()
    career_cluster = pd.read_csv("static/All_Career_Clusters.csv")
    all_job = json.dumps(career_cluster['Occupation'].tolist())


    for i in range(len(job_details)):
        if job_details.iloc[i, 0] == job:
            job_details = job_details.iloc[i, 1]
            job_details_1 = job_details.replace("\n", "<br>")
            return render(request, 'admin/details.html', {"job_details": job_details, "job": job,"single_graph":single_graph,"all_job":all_job,"trend_value":trend_value,"change":round(change,1),"career_category":list(career_category)})

    

@login_required
def find(request):
    data = request.GET.get('param')
    job = unquote(data)
    job = job.replace("amp;", "")
    
    career_cluster = pd.read_csv("static/All_Career_Clusters.csv")

    career_category = ["Agriculture, Food & Natural Resources","Transportation, Distribution & Logistics","Architecture & Construction","Science, Technology, Engineering & Mathematics","Health Science","Business Management & Administration","Hospitality & Tourism","Education & Training","Human Services","Finance","Information Technology","Government & Public Administration","Law, Public Safety, Corrections & Security","Manufacturing","Marketing"]
    career_category.sort()


    job_patents_timeseries = pd.read_csv("static/job_patents_timeseries_newprepro_fbfore.csv")
    job_trend = pd.read_csv("static/job_patent_trend_newprepro.csv")
    max_list = {}
    for i in range(len(career_cluster)):
        if career_cluster.iloc[i, 0] == job:
            for col in job_trend.columns:
                if col in job_patents_timeseries.columns and col == career_cluster.iloc[i, 3]:
                    job_trend_list = job_trend[col].tolist()
                    max_list.update({col: job_trend_list})


    sorted_dict = dict(sorted(max_list.items(), key=lambda x: x[1][4], reverse=True))
    predicted_job_1 = {k: sorted_dict[k] for k in list(sorted_dict)[:6]}
    predicted_job = dict(sorted(predicted_job_1.items(), key=lambda x: x[1][1], reverse=True))
    trend = []
    for i in predicted_job.values():
        trend.append({'trend_value': i[0], 'change': i[1:]})
    #return HttpResponse(trend, content_type='application/json')
    myList_data = {}
    for i in predicted_job.keys():
        myList_data.update({i: job_patents_timeseries[i].tolist()})
    myList_data_4 = []
    for i,j in predicted_job.items():
        types = 0
        if j[0] == 0:
            types = 0
        elif j[0] == 1:
            types = 1
        elif j[0] == -1:
            types = -1

        myList_data_4.append({'name': i, 'trend_value': types, 'change': round(j[1:][0],1)})
    myList_data_1 = []
    for i,j in myList_data.items():
        myList_data_1.append({'name': i, 'data': j})
    all_job = json.dumps(career_cluster['Occupation'].tolist())
   # return HttpResponse(all_job, content_type='application/json')
    return render(request, 'admin/pages.html', {"job":job,"myList_data": myList_data_1,"trend":myList_data_4,"career_category": list(career_category),"all_job":all_job})


@login_required
def skill(request):
    user_skills = ["Time Management","Active Listening","Programming"]
    min_imp=3
    job_skills = {}
    with open('static/skill_list.json', 'r') as fp:
        job_skills = json.load(fp)

    json_data = json.dumps(list(job_skills))
    # suitable_job_score = []
    # for job,skills in job_skills.items():
    #     matched_skills = set(user_skills).intersection(skills.keys())
    #     total_importance = sum(skills[skill]["Importance"] for skill in matched_skills if skills[skill]["Importance"]>=min_imp)

    #     if total_importance > min_imp:
    #         suitable_job_score.append((job,total_importance))

    # suitable_job_score.sort(key=lambda x: x[1], reverse=True)
    #return HttpResponse(JsonResponse(dict(suitable_job_score)))
    return render(request, 'admin/skill.html', {"suitable_job_score": json_data})

@login_required
def skill_details(request):
    if request.method == 'POST':
        job_trend = pd.read_csv("static/job_patent_trend_newprepro.csv",index_col=0)
        job_patents_timeseries = pd.read_csv("static/job_patents_timeseries_newprepro_fbfore.csv",index_col=0)

        user_skills = request.POST.getlist('skill')
        if len(user_skills) > 0:
            min_imp=3
            with open('static/job_skills_del.json', 'r') as fp:
                    job_skills = json.load(fp)

            suitable_job_score = []
            for job,skills in job_skills.items():
                matched_skills = set(user_skills).intersection(skills.keys())
                total_importance = sum(skills[skill]["Importance"] for skill in matched_skills if skills[skill]["Importance"]>=min_imp)

                if total_importance > min_imp:
                    suitable_job_score.append((job,total_importance))

            suitable_job_score.sort(key=lambda x: x[1], reverse=True)

            suitable_job_score = [{"job_title":job,"score":score,"per_change":round(job_trend[job].iloc[1],2),"timeseries":job_patents_timeseries[job].tolist()} for job,score in suitable_job_score if job in job_patents_timeseries and job_trend[job].loc["trend"] == 1]

            #return HttpResponse(suitable_job_score[:20])
            return render(request, 'admin/skill_list.html', {"suitable_job_score": suitable_job_score[:21]})
        