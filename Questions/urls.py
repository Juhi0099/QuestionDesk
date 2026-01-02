from django.urls import path
from Questions.views import *

urlpatterns = [
    path('create/question-set/', create_question_set_view, name='create-question-set-view'),
    path('list/all/question-set/', list_question_set_view, name='list-question-set-view'),
    path('update/question-set/<int:question_set_id>/', update_question_set_view, name='update-question-set-view'),
    path('delete/question-set/<int:id>/<int:unit_no>/', delete_question_set_view, name='delete-question-set-view'),
    path('delete/all/question-set/<int:id>/', delete_all_question_set_view, name='delete-all-question-set-view'),

    path('create/question/<int:id>/', create_question_view, name="create-question-view"),
    path('list/question/<int:question_set_id>/', list_question_view, name="list-question-view"),
    path('update/question/<int:id>/<int:unit_no>/', update_question_view, name="update-question-view"),
]
