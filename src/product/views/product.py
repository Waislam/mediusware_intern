from django.views import generic
from datetime import date

from product.models import Variant, Product, ProductVariantPrice, ProductVariant
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context


class ProductListView(generic.TemplateView):
    template_name = 'products/list.html'

    def name_search(self, product_name):
        query = Product.objects.filter(title__icontains=product_name)
        return query

    def created_at_search(self, created_at):
        time_list = str(created_at).split('-')
        year = int(time_list[0])
        month = int(time_list[1])
        day = int(time_list[2])
        result = Product.objects.filter(created_at__contains=date(year, month, day))
        return result

    def price_range_search(self, price_from, price_to):
        query = (Q(productvariantprice__price__gte=price_from)) & (Q(productvariantprice__price__lte=price_to))
        result = Product.objects.filter(query)
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        # handle filtering
        product_name = self.request.GET.get('title')
        vari_title = self.request.GET.get('variant')
        created_at = self.request.GET.get('date')
        price_from = self.request.GET.get('price_from')
        price_to = self.request.GET.get('price_to')
        if product_name:
            product_list = self.name_search(product_name)
        elif created_at:
            product_list = self.created_at_search(created_at)
        elif price_from and price_to:
            product_list = self.price_range_search(price_from, price_to)
        elif vari_title != None:
            product_list = Product.objects.filter(productvariant__variant_title=vari_title)
        else:
            product_list = Product.objects.all()
        # context['products'] = product_list
        product_variant_price = ProductVariantPrice.objects.all()
        context['product_variant_price_list'] = product_variant_price

        # handle pagination
        page_number = self.request.GET.get('page')
        paginator = Paginator(product_list, 2)
        total_page = paginator.num_pages
        try:
            current_page_data = paginator.page(page_number)
        except EmptyPage:
            current_page_data = paginator.page(total_page)
        except:
            current_page_data = paginator.page(1)

        context['products'] = current_page_data
        page_list = [page for page in range(1, total_page+1)]
        context['page_list'] = page_list
        context['total_products'] = paginator.count
        context['page_start_index'] = current_page_data.start_index()
        context['page_end_index'] = current_page_data.end_index()

        # variant title and subtitle handling
        variant_list = Variant.objects.filter(active=True).values('id', 'title')
        product_variant_list = ProductVariant.objects.all()
        list_of_variant_dict = []

        for variant in variant_list:
            dict_of_variant = dict()
            sub_title_list = list()
            dict_of_variant['title'] = variant['title']
            for p_variant in product_variant_list.filter(variant=variant['id']):
                sub_title_list.append(p_variant.variant_title)
            unique = list(set(sub_title_list))
            dict_of_variant['sub_titles'] = unique
            list_of_variant_dict.append(dict_of_variant)
        context['variant_title_sub_title'] = list_of_variant_dict

        return context