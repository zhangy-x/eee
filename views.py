import os

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.urls import reverse

from  employee.models import Employee
from django.db import transaction
from django.shortcuts import render, HttpResponse, redirect
import uuid
# Create your views here.

def emplist(request):

    emps = Employee.objects.all()
    pagtor = Paginator(emps, per_page=3)

    numbers = request.session.get("numbers")
    if numbers:
        number = numbers
        del request.session["numbers"]
    else:
        number = request.GET.get("number", 1)

    try:
        page = pagtor.page(number)
    except:
        page = pagtor.page(1)

    finally:
        msg = request.GET.get("msg")
        if msg:
            return render(request, "../static/../templates/employee/emplist.html", {"page": page, "msg": msg})
        return render(request, "../static/../templates/employee/emplist.html", {"page": page})
# 前后端分离
def addemp(request):
    return render(request, "../static/../templates/employee/addEmp.html")

def addlogic(request):
    try:
        with transaction.atomic():
            name = request.POST.get("name")
            age = request.POST.get("age")
            salary = request.POST.get("salary")
            birthday = request.POST.get("birthday")
            headpic = request.FILES.get("headpic")
            # 修改头像的原文件名
            headpic.name = str(uuid.uuid4()) + os.path.splitext(headpic.name)[1]
            emp = Employee.objects.create(name=name,age=age,birthday=birthday,salary=salary,headpic=headpic)
            print(emp)
            if emp:
                pagtor = Paginator(Employee.objects.all(),per_page=3)
                request.session["numbers"] = pagtor.num_pages
                return JsonResponse({"error": 0, "msg": "添加成功"})
    except Exception as e:
        print(e)
        return JsonResponse({"error":1,"msg":"添加失败"})

def updateemp(request):
    id = request.GET.get("id")
    number = request.GET.get("number") #当前的页号
    request.session["numbers"] = number
    try:
        emp = Employee.objects.get(pk=id)
        return render(request, "../static/../templates/employee/updateEmp.html", {"emp": emp})
    except:
        return render(request, "../static/../templates/employee/updateEmp.html")

def updatelogic(request):
    try:
        with transaction.atomic():
            id = request.POST.get("id")
            name = request.POST.get("name")
            age = request.POST.get("age")
            salary = request.POST.get("salary")
            birthday = request.POST.get("birthday")
            emp = Employee.objects.get(pk=id)
            emp.name = name
            emp.age = age
            emp.salary = salary
            emp.birthday = birthday

            headpic = request.FILES.get("headpic")
            if headpic:
                headpic.name = str(uuid.uuid4()) + os.path.splitext(headpic.name)[1]
                emp.headpic = headpic

            emp.save()
            return JsonResponse({"error":0,"msg":"更新成功"})
    except Exception as e:
        print(e)
        return JsonResponse({"error":1,"msg":"更新失败"})

def delete(request):
    try:
        with transaction.atomic():
            id = request.GET.get("id")
            emp = Employee.objects.get(pk=id)
            emp.delete()
            num = int(request.GET.get("number")) # 当前页号 3
            pagtor = Paginator(Employee.objects.all(),per_page=3)
            if num > pagtor.num_pages:
                num -= 1
            request.session["numbers"] = num
            return JsonResponse({"error":0,"msg":"删除成功"})
    except Exception as e:
        print(e)
        return JsonResponse({"error": 1, "msg": "删除失败"})