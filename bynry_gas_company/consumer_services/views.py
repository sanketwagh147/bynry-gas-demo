from urllib import request
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.edit import FormView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from django.urls import reverse
from django.shortcuts import redirect
from .models import ServiceRequests
from .forms import ServiceRequestUpdateForm

from consumer_services.models import BynryUser
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import auth, messages

# Create your views here.
from .forms import BynryUserForm, ServiceRequestForm
from .models import FileUpload, ServiceRequests


def consumer_home(request):
    context = {}
    return render(request, "consumer_services/main.html", context)

def sign_up(request):
    if request.method == "POST":
        form = BynryUserForm(request.POST)
        if form.is_valid():
            # Create the user using form
            # user = form.save(commit=False)
            # password = form.cleaned_data["password"]
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # user.save()

            # Create user using create_user method
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            phone_number = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = BynryUser.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
                phone_number=phone_number,
            )
            user.role = BynryUser.CUSTOMER
            user.save()

            # Send verification email

            return redirect("consumer_sign_up")
        else:
            print("invalid form")
            print(form.errors)
            context = {"form": form}
            return render(request, "consumer_services/sign_up.html", context=context)

    else:
        form = BynryUserForm()
        context = {"form": form}
        return render(request, "consumer_services/sign_up.html", context)

def login(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already Logged in")
        return redirect("myRequests")

    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in")
            print(messages)
            return redirect("myRequests")
        else:
            messages.error(request, "Invalid Login credentials")
            print(messages)
            return redirect("login")
    return render(request, "consumer_services/sign_in.html")
def detect_user(user):
    if user.role == 1:
        redirect_url = "customerRequests"
    elif user.role == 2:
        redirect_url = "userRequests"
    elif user.role == None and user.is_superadmin:
        redirect_url = "/admin"
    else:
        redirect_url = ""

    return redirect_url
@login_required(login_url="login")
def myRequests(request):
    user = request.user
    redirect_url = detect_user(user)
    return redirect(redirect_url)
    # context = {}
    # return render(request, "consumer_services/requests.html", context)

@login_required(login_url="login")
def customerRequests(request):
    user = request.user
    context = {}
    return render(request, "consumer_services/requests_cust.html", context)

@login_required(login_url="login")
def userRequests(request):
    user = request.user
    context = {}
    # return render(request, "consumer_services/requests_user.html", context)
    return redirect("create_service_request")


def logout(request):
    auth.logout(request)
    messages.info(request, "You are now logged out")
    return redirect("login")


# def create_service_request(request):
#     if request.method == 'POST':
#         form = ServiceRequestForm(request.POST, request.FILES)
#         if form.is_valid():
#             service_request = form.save()
#             return redirect('success_view')
#     else:
#         form = ServiceRequestForm()
#     return render(request, 'consumer_services/service_request_form.html', {'form': form})


class ServiceRequestView(LoginRequiredMixin,FormView):
    login_url = 'login'
    form_class = ServiceRequestForm
    template_name = 'consumer_services/service_request_form.html'  # Replace with your template.
    success_url = "/service_requests/"

    def form_valid(self, form):
            file_arr = []
            form.instance.requested_by = self.request.user 
            for each in form.cleaned_data['attachments']:
                pk_id = FileUpload.objects.create(file=each)
                file_arr.append(pk_id.pk)

            form.instance.files= file_arr

            form.save()
            return super(ServiceRequestView, self).form_valid(form)

class ServiceRequestListView(LoginRequiredMixin,ListView):
    login_url = 'login'
    model = ServiceRequests
    template_name = 'consumer_services/service_request_list.html'
    context_object_name = 'service_requests'  # This will be used in the template
    ordering = ['-created_at', 'updated_at']

    

    def get_queryset(self):
        print(self)
        if self.request.user.role != 1:
            return ServiceRequests.objects.filter(requested_by=self.request.user).order_by('-updated_at')
        else: 
            return ServiceRequests.objects.all().order_by('-updated_at')
    
def create_service_request(request):
    if request.method == 'POST':
         form = ServiceRequestForm(request.POST, request.FILES)
         files = request.FILES.getlist('files')
         if form.is_valid():
             for f in files:
                 file_instance = ServiceRequestForm(files=f)
                 file_instance.save()
    else:
         form = ServiceRequestForm()

    return render(request, "consumer_services/service_request_form.html", {'form': form})


class ServiceRequestDetailView(FormMixin, DetailView):
    model = ServiceRequests
    template_name = 'consumer_services/service_request_detail.html'
    form_class = ServiceRequestUpdateForm

    def get_success_url(self):
        return reverse('service_request_list', )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            # Update the current status and priority
            self.object.current_status = form.cleaned_data['current_status']
            self.object.priority = form.cleaned_data['priority']
            self.object.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
