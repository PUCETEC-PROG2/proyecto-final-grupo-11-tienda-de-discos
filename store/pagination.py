from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

class PaginationMixin:
    items_per_page = 10

    def paginate_queryset(self, queryset, request):
  
        page = request.GET.get('page', 1)
        paginator = Paginator(queryset, self.items_per_page)
        
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
            
        return page_obj, paginator