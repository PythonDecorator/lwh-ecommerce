from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, DeleteView

from dashboard.mixins import StaffAndLoginRequiredMixin
from home.forms import ReviewForm
from items.forms import ItemCreateEditForm, CategoryForm
from items.models import Item, Category, Review
from items.utils import query_items


class ItemsListView(ListView):
    model = Item
    queryset = Item.objects.active_items()
    template_name = 'item/items.html'
    paginate_by = 15

    def get_queryset(self):
        query = self.request.GET.get('search', None)
        item = Item.objects.active_items()
        category = self.request.GET.get('category', None)
        if query:
            object_list = query_items(query, item)
        elif category:
            print('checking Category')
            object_list = item.filter(category__icontains=category)
        else:
            object_list = Item.objects.active_items()
        return object_list


class FeaturedListView(ListView):
    model = Item
    queryset = Item.objects.featured_items()
    template_name = 'item/items.html'
    paginate_by = 15


class ItemsDetailView(DetailView):
    model = Item
    queryset = Item.objects.active_items()
    template_name = 'item/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = context['object']
        item.view_count += 1
        item.save()
        related_items = Item.objects.filter(category=item.category)[:10]
        context['related_items'] = related_items
        context['review_form'] = ReviewForm()
        return context


class CategoryView(View):
    def get(self, request, *args, **kwargs):
        id = kwargs.pop('id')
        page = request.GET.get('page', 1)
        category = Category.objects.filter(id=id).first()
        if not category:
            return render(request, 'errors/404.html', {})
        items = Item.objects.filter(category=category)
        paginator = Paginator(items, 15)
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        return render(request, 'item/category.html', {'items': items, 'category': category})


class SaveReviewView(View):
    def post(self, request):
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            if request.user.is_authenticated:
                form.user = request.user
            form.save()
            messages.info(
                self.request, "Thanks for the review")
        else:
            messages.warning(
                self.request, "An error occurred")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class DeleteReview(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        id = request.POST.get('review_id')
        review = Review.objects.filter(id=id).first()
        if not review:
            messages.warning(
                self.request, "An error occurred")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if request.user.is_superuser or review.user == request.user:
            review.delete()
            messages.success(request, 'Review was deleted')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ItemCreateView(StaffAndLoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        form = ItemCreateEditForm()
        page = self.request.GET.get('page')
        items = Item.objects.active_items()
        paginator = Paginator(items, 15)
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        return render(self.request, 'dashBoard/item/create_update_item.html',
                      {'form': form,
                       'items': items,
                       'title': 'Create Product', 'action': 'Create'})

    def post(self, *args, **kwargs):
        form = ItemCreateEditForm(self.request.POST, self.request.FILES or None)
        form.image = self.request.POST.get('image')
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = self.request.user
            instance.save()
            messages.success(self.request, 'item was saved')
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

        elif not form.is_valid():
            messages.error(self.request, 'invalid form data')
        return redirect('items:item_create')


class ItemUpdateView(StaffAndLoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        item_id = kwargs['id']
        page = self.request.GET.get('page')
        item = get_object_or_404(Item, id=item_id)
        form = ItemCreateEditForm(instance=item)
        items = Item.objects.active_items().order_by('id')
        paginator = Paginator(items, 15)
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        return render(self.request, 'dashboard/item/create_update_item.html',
                      {'form': form, 'items': items, 'title': 'Update Product', 'action': 'Update'})

    def post(self, *args, **kwargs):
        item_id = kwargs['id']
        item = get_object_or_404(Item, id=item_id)
        form = ItemCreateEditForm(self.request.POST, self.request.FILES or None, instance=item)
        form.image = self.request.POST.get('image')
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = self.request.user
            instance.save()
            messages.success(self.request, 'item was saved')
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

        elif not form.is_valid():
            messages.error(self.request, 'invalid form data')
        return redirect('items:item_create')


class ItemDeleteView(StaffAndLoginRequiredMixin, DeleteView):
    model = Item
    success_url = reverse_lazy('items:item_create')
    template_name = 'dashboard/item/delete_item.html'
    context_object_name = 'item'


class ActiveItemsListView(StaffAndLoginRequiredMixin, ListView):
    model = Item
    paginate_by = 50
    context_object_name = "items"
    template_name = "dashboard/item/items.html"

    def get_queryset(self):
        query = self.request.GET.get('search')
        item = Item.objects.active_items()
        if query:
            object_list = query_items(query, item)
            return object_list
        else:
            object_list = Item.objects.filter(is_active=True)
            return object_list


class InActiveItemsListView(StaffAndLoginRequiredMixin, ListView):
    model = Item
    paginate_by = 50
    context_object_name = "items"
    template_name = "dashboard/item/items.html"

    def get_queryset(self):
        query = self.request.GET.get('search')
        item = Item.objects.in_active_items()
        if query:
            object_list = query_items(query, item)
            return object_list
        else:
            object_list = Item.objects.in_active_items()
            return object_list


class ActiveAndInActiveItemsListView(StaffAndLoginRequiredMixin, ListView):
    model = Item
    paginate_by = 50
    context_object_name = "items"
    template_name = "dashboard/item/items.html"

    def get_queryset(self):
        query = self.request.GET.get('search')
        item = Item.objects.all()
        if query:
            object_list = query_items(query, item)
            return object_list
        else:
            object_list = Item.objects.active_items()
            return object_list


class CategoryCreateListView(StaffAndLoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        form = CategoryForm()
        page = self.request.GET.get('page')
        items = Category.objects.all()
        paginator = Paginator(items, 15)
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        return render(request, 'dashboard/category/list_create.html',
                      {'form': form,
                       'items': items, })

    def post(self, request, *args, **kwargs):
        form = CategoryForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created")
        else:
            messages.error(request, 'An error occurred')
        return redirect('items:dashboard_category_list_create')


class CategoryDeleteView(StaffAndLoginRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('items:dashboard_category_list_create')
    template_name = 'dashboard/category/category_delete.html'
    context_object_name = 'item'
