from django.contrib import messages
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
# Create your views here.
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DeleteView

from dashboard.mixins import StaffAndLoginRequiredMixin
from home.forms import ContactForm, FaqForm, DashboardContactForm
from home.models import Faq, Contact, SubscribeEmail
from home.tasks import send_support_message, send_customers_message
from home.utils import get_reviews
from items.models import Item
from orders.models import Coupon
from orders.utils import get_or_create_customer


def signup_redirect_view(View):
    return redirect('home:home_page')


def view_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def view_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)


def view_400(request, exception=None):
    return render(request, 'errors/400.html', status=400)


def view_500(request, exception=None):
    return render(request, 'errors/500.html', status=500)


class HomePageView(View):

    def get(self, request, *args, **kwargs):
        reviews = get_reviews()

        customer = get_or_create_customer(request)
        context = {
            'Item': Item.objects.active_items()[:10],
            'Featured': Item.objects.featured_items()[:10],
            'Testimonials': reviews
        }
        return render(request, 'index.html', context)



class TermsPageView(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'home/terms_and_condition.html', )


class PrivacyPolicyPageView(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'home/privacy_policy.html', )


class ShippingPolicyPageView(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'home/shipping_policy.html', )


class RefundPolicyPageView(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'home/refund_policy.html', )


class SubscribeView(View):
    def post(self, request):
        email = request.POST.get('subscribe_email')
        if email:
            if SubscribeEmail.objects.filter(email=email).exists():
                messages.success(request, 'Email has already been subscribed')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            SubscribeEmail.objects.create(email=email)
            messages.success(request, 'Successfully subscribed')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ContactView(View):

    def get(self, request):
        form = ContactForm()
        return render(request, 'home/contact.html', {'form': form})

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            send_support_message(
                form.cleaned_data.get('subject'),
                form.cleaned_data.get('message'))
            messages.success(request, 'Successfully sent message we would be in touch.')
        else:
            messages.error(request, 'An error occurred try again later.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class AboutView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'home/about.html', {'Testimonials': get_reviews()})


class OffersListView(ListView):
    model = Coupon
    queryset = Coupon.objects.all()
    template_name = 'home/offer.html'


class FaqView(View):
    def get(self, request, *args, **kwargs):
        Faqs = Faq.objects.all()
        return render(request, 'home/faq.html', {'Faqs': Faqs})


class FaqCreateListView(StaffAndLoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        form = FaqForm()
        page = self.request.GET.get('page')
        items = Faq.objects.all()
        paginator = Paginator(items, 15)
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        return render(request, 'dashboard/faq/list_create.html',
                      {'form': form,
                       'items': items, })

    def post(self, request, *args, **kwargs):
        form = FaqForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            form.save()
            messages.success(request, "Faq created")
        else:
            messages.error(request, 'An error occurred')
        return redirect('home:dashboard_faq_list_create')


class FaqDeleteView(StaffAndLoginRequiredMixin, DeleteView):
    model = Faq
    success_url = reverse_lazy('home:dashboard_faq_list_create')
    template_name = 'dashBoard/faq/faq_delete.html'
    context_object_name = 'item'


class DashboardContactCreateListView(StaffAndLoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        form = DashboardContactForm()
        search = request.GET.get('search')
        items = Contact.objects.all()
        if search:
            items = items.filter(
                Q(name__icontains=search) |
                Q(subject__icontains=search) |
                Q(message__icontains=search)
            )
        page = self.request.GET.get('page')
        paginator = Paginator(items, 15)
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        return render(request, 'dashboard/contact/list_create.html',
                      {
                          'form': form,
                          'items': items, }
                      )

    def post(self, request, *args, **kwargs):
        form = DashboardContactForm(request.POST)
        print(request.POST)
        if form.is_valid():
            print('passed here')
            if form.cleaned_data.get('email') or form.cleaned_data.get('all_customers'):
                send_customers_message(
                    form.cleaned_data.get('email'),
                    form.cleaned_data.get('all_customers'),
                    form.cleaned_data.get('subject'),
                    form.cleaned_data.get('message'))
                messages.success(request, 'Successfully sent message we would be in touch.')
                print("sent")
        else:
            messages.error(request, 'An error occurred please submit the right details')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class DashboardContactDeleteView(StaffAndLoginRequiredMixin, DeleteView):
    model = Contact
    success_url = reverse_lazy('home:dashboard_contact_list_create')
    context_object_name = 'item'


class DashboardContactDetailView(StaffAndLoginRequiredMixin, DeleteView):
    model = Contact
    queryset = Contact.objects.all()
    template_name = 'dashboard/contact/contact_detail.html'
