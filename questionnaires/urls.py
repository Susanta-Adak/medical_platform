from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from . import views_builder

app_name = 'questionnaires'

urlpatterns = [
    # Questionnaire URLs
    path('', views.QuestionnaireListView.as_view(), name='list'),
    path('create/', views.QuestionnaireCreateView.as_view(), name='create'),
    path('<int:pk>/', views.QuestionnaireDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.QuestionnaireUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.QuestionnaireDeleteView.as_view(), name='delete'),
    path('<int:pk>/clone/', views_builder.clone_questionnaire, name='clone'),
    path('<int:pk>/toggle-visibility/', views_builder.toggle_visibility, name='toggle_visibility'),
    path('<int:pk>/start/', views.questionnaire_start, name='questionnaire_start'),
    path('thank-you/<int:pk>/', views.questionnaire_thank_you, name='questionnaire_thank_you'),
    
    # File upload endpoint
    path('upload-attachment/', views.upload_attachment, name='upload_attachment'),
    
    # Builder views
    path('builder/', views_builder.QuestionnaireBuilderView.as_view(), name='builder'),
    path('builder/list/', views_builder.questionnaire_list_builder, name='builder_list'),
    path('builder/<int:pk>/edit/', views_builder.edit_questionnaire_builder, name='builder_edit'),
    # API endpoints
    path('api/save/', views_builder.save_questionnaire_api, name='save_api'),
    path('api/update-question-order/', views.update_question_order, name='update_question_order'),
    path('api/list/', views.api_list_questionnaires, name='api_list'),
    
    # Simple builder (legacy)
    path('simple-builder/', views.simple_questionnaire_builder, name='simple_builder'),
    
    # Question URLs
    path('questions/create/<int:questionnaire_id>/', views.QuestionCreateView.as_view(), name='question_create'),
    path('questions/<int:pk>/update/', views.QuestionUpdateView.as_view(), name='question_update'),
    path('questions/<int:pk>/delete/', views.QuestionDeleteView.as_view(), name='question_delete'),
    
    # Response URLs
    path('responses/', views.ResponseListView.as_view(), name='response_list'),
    path('responses/<int:pk>/', views.ResponseDetailView.as_view(), name='response_detail'),
    path('responses/<int:pk>/delete/', views.ResponseDeleteView.as_view(), name='response_delete'),
    path('responses/<int:pk>/api-update/', views.api_update_response, name='api_update_response'),
    path('responses/<int:pk>/edit-form/', views.get_response_edit_form, name='api_get_edit_form'),
    path('download-responses/', views.download_responses, name='download_responses'),
    
    # API URLs
    path('api/questions/order/', views.update_question_order, name='update_question_order'),

    # Public flow (optional)
    path('<int:pk>/start/', views.questionnaire_start, name='questionnaire_start'),
    path('thank-you/<int:pk>/', views.questionnaire_thank_you, name='questionnaire_thank_you'),
]
