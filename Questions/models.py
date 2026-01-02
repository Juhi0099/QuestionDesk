from django.db import models
from Users.models import *
# Create your models here.

class QuestionSet(models.Model):
    id = models.BigAutoField(primary_key=True)
    subject = models.ForeignKey(Subject, related_name='question_sets', on_delete=models.CASCADE)
    unit_no = models.PositiveIntegerField(null=False, blank=False, default=1) 
    unit_title = models.CharField(max_length=255, null=False, blank=False)
    co_no = models.PositiveIntegerField(null=False, blank=False, default=1)
    co_title = models.CharField(max_length=255, null=False, blank=False)
    created_by = models.ForeignKey(User, related_name='question_sets', on_delete=models.CASCADE)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.subject.code} - {self.subject.name} - Unit: {self.unit_no}'

    class Meta:
        db_table = 'Question Sets Table'

class Question(models.Model):
    id = models.BigAutoField(primary_key=True)
    question_set = models.ForeignKey(QuestionSet, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=255, null=False, blank=False) 
    mark = models.PositiveIntegerField(null=False, blank=False, default=0) 
    level = models.CharField(max_length=255, null=True, blank=True, default='') 

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'Questions Table'
