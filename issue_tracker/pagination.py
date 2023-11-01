from django.core.paginator import Paginator


def paginate(objects, per_page:int, page_number:int):
    paginator = Paginator(objects, per_page, allow_empty_first_page=True)    
    return paginator.get_page(page_number)