from django.shortcuts import render
from django.views.generic import TemplateView
from .models import QA

class FaqView(TemplateView):
    template_name = 'faq.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['qa_data'] = QA.objects.all()
        return context
