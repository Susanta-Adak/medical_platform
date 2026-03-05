from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages
from django.db.models import Q
from accounts.models import User
from patients.models import Patient
from questionnaires.models import Response, Questionnaire

class DoctorRequiredMixin(LoginRequiredMixin):
    """Mixin to ensure user is a Doctor"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.DOCTOR:
            messages.error(request, 'Access denied. Doctor role required.')
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

@login_required
def doctor_home(request):
    """Doctor dashboard home page"""
    if request.user.role != User.Role.DOCTOR:
        messages.error(request, 'Access denied. Doctor role required.')
        return redirect('login')
    
    # Get statistics for the dashboard
    total_patients = Patient.objects.count()
    total_responses = Response.objects.count()
    recent_responses = Response.objects.select_related('patient', 'questionnaire').order_by('-submitted_at')[:10]
    
    context = {
        'total_patients': total_patients,
        'total_responses': total_responses,
        'recent_responses': recent_responses,
    }
    return render(request, 'doctor/home.html', context)

class PatientListView(DoctorRequiredMixin, ListView):
    model = Patient
    template_name = 'doctor/patient_list.html'
    context_object_name = 'patients'
    paginate_by = 20

    def get_queryset(self):
        queryset = Patient.objects.all().order_by('-created_at')
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(patient_id__icontains=q)
            )
        return queryset

class PatientDetailView(DoctorRequiredMixin, DetailView):
    model = Patient
    template_name = 'doctor/patient_detail.html'
    context_object_name = 'patient'

class ResponseListView(DoctorRequiredMixin, ListView):
    model = Response
    template_name = 'doctor/response_list.html'
    context_object_name = 'responses'
    paginate_by = 20

    def get_queryset(self):
        return Response.objects.select_related('patient', 'questionnaire', 'respondent').order_by('-submitted_at')

class ResponseDetailView(DoctorRequiredMixin, DetailView):
    model = Response
    template_name = 'doctor/response_detail.html'
    context_object_name = 'response'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vitals'] = self.object.patient.vitals.order_by('-recorded_at').first()
        return context
