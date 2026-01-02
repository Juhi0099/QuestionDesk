from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Min
from Questions.models import *
from Questions.services import *
# Create your views here.

def create_question_set_view(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        subject = Subject.objects.filter(code=code).first()
        unit_no = request.POST.get('unit_no')
        unit_title = request.POST.get('unit_title')
        co_no = request.POST.get('co_no')
        co_title = request.POST.get('co_title')

        if QuestionSet.objects.filter(subject=subject, unit_no=unit_no).exists():
            return JsonResponse({'status':'error', 'message':f'Question Set for Unit No: {unit_no} already exists'})
        if QuestionSet.objects.filter(subject=subject, co_no=co_no).exists():
            return JsonResponse({'status':'error', 'message':f'Question Set for CO No: {co_no} already exists'})

        question_set = QuestionSet.objects.create(created_by=request.user, subject=subject, unit_no=unit_no, unit_title=unit_title, co_no=co_no, co_title=co_title)
        messages.success(request, f'Question set for {subject.name}, Unit {unit_no} created successfully.')
        return JsonResponse({'status':'success', 'success_url':f'/create/question/{question_set.id}/'})
    subjects = request.user.profile.subjects.all()
    return render(request, 'question_sets/create_question_set.html', context={'subjects':subjects})

def list_question_set_view(request):
    distinct_question_set_subjects = Subject.objects.filter(
        question_sets__in=QuestionSet.objects.filter(created_by=request.user)
    ).distinct().annotate(min_unit_no=Min('question_sets__unit_no'))
    return render(request, 'question_sets/list_question_set.html', context={'subjects':distinct_question_set_subjects})

def update_question_set_view(request, question_set_id):
    question_set = QuestionSet.objects.get(id=question_set_id)
    
    if request.method == 'POST':
        code = request.POST.get('code')
        subject = Subject.objects.filter(code=code).first()
        unit_no = request.POST.get('unit_no')
        unit_title = request.POST.get('unit_title')
        co_no = request.POST.get('co_no')
        co_title = request.POST.get('co_title')

        question_sets = QuestionSet.objects.filter(subject=subject, unit_no=unit_no)
        if question_sets.exists():
            if question_sets[0] != question_set:
                return JsonResponse({'status':'error', 'message':f'Question Set for Unit No: {unit_no} already exists'})
        question_sets = QuestionSet.objects.filter(subject=subject, co_no=co_no)
        if question_sets.exists():
            if question_sets[0] != question_set:
                return JsonResponse({'status':'error', 'message':f'Question Set for CO No: {co_no} already exists'})

        question_set.subject = subject
        question_set.unit_no = unit_no
        question_set.unit_title = unit_title
        question_set.co_no = co_no
        question_set.co_title = co_title
        question_set.save()
        messages.success(request, f'Question set for {subject.name}, Unit {unit_no} updated successfuully.')
        return JsonResponse({'status':'success', 'success_url':f'/update/question-set/{question_set.id}/'})

    subjects = request.user.profile.subjects.all()
    return render(request, 'question_sets/update_question_set.html', context={'question_set':question_set,'subjects':subjects})

def delete_question_set_view(request, id, unit_no):
    subject = Subject.objects.get(id=id)
    question_set = QuestionSet.objects.get(subject=subject, unit_no=int(unit_no))
    print(question_set,"QS")
    question_set.delete()
    messages.success(request, f'Question set for {subject},Unit {unit_no} deleted successfully.')
    remaining_units = QuestionSet.objects.filter(subject=subject).values_list('unit_no', flat=True)
    if remaining_units:
        remaining_units = sorted([int(u) for u in remaining_units])
        unit = int(unit_no)
        closest_unit = min(remaining_units, key=lambda x: abs(x - unit))
        return redirect('update-question-view', id=id, unit_no=closest_unit)
    else:
        return redirect('list-question-set-view')

def delete_all_question_set_view(request, id):
    subject = Subject.objects.get(id=id)
    question_sets = QuestionSet.objects.filter(subject=subject)
    question_sets.delete()
    messages.success(request, f'Question sets for {subject} deleted successfully.')
    return redirect('list-question-set-view')

def create_question_view(request, id):
    question_set = QuestionSet.objects.get(id=id)
    if request.method == 'POST':
        question_titles = request.POST.getlist('question_title[]')
        marks = request.POST.getlist('mark[]')
        for title, mark in zip(question_titles, marks):
            level = classify_blooms_taxonomy(title)
            Question.objects.create(title=title, mark=mark, level=level, question_set=question_set)
        messages.success(request, f'Questions added for {question_set.subject} - Unit:{question_set.unit_no}.')
        return JsonResponse({'status':'success', 'success_url':f'/update/question/{question_set.subject.id}/{question_set.unit_no}/'})
    return render(request, 'question_sets/create_question.html', context={'question_set':question_set})

def list_question_view(request, question_set_id):
    question_set = QuestionSet.objects.get(id=question_set_id)
    questions = Question.objects.filter(question_set=question_set).all()
    return render(request, 'question_sets/list_question.html', context={'question_set':question_set,'questions':questions})

def update_question_view(request, id, unit_no):
    subject = Subject.objects.get(id=id)
    question_set = QuestionSet.objects.get(subject=subject, unit_no=unit_no)
    
    if request.method == 'POST':
        Question.objects.filter(question_set=question_set).delete()
        question_titles = request.POST.getlist('question_title[]')
        marks = request.POST.getlist('mark[]')
        for title, mark in zip(question_titles, marks):
            level = classify_blooms_taxonomy(title)
            Question.objects.create(title=title, mark=mark, level=level, question_set=question_set)
        messages.success(request, f'Question updated for Question set for {question_set.subject.name}, Unit:{question_set.unit_no}.')
        return JsonResponse({'status':'success', 'success_url':f'/update/question/{question_set.subject.id}/{question_set.unit_no}/'})

    question_sets =QuestionSet.objects.filter(subject=subject)
    units = question_sets.values_list('unit_no', flat=True)
    questions = Question.objects.filter(question_set=question_set).all().order_by('mark','level')
    return render(request, 'question_sets/update_question.html', context={'question_set':question_set,'questions':questions, 'units':units, 'current_unit':int(unit_no)})

