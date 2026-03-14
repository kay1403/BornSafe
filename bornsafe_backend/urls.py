
# Templates (interface web)
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from actes.views_templates import dashboard

urlpatterns += [
    path('', login_required(TemplateView.as_view(template_name='dashboard.html')), name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('actes/', include('actes.urls_templates')),
    path('provinces/', include('provinces.urls_templates')),
    path('comptes/', include('accounts.urls_templates')),
]
