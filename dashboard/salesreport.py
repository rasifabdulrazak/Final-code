from django.shortcuts import render, redirect, HttpResponse
from app.models import *
from app.forms import LoginForm
from django.contrib.auth import authenticate
from .models import *
from django.db.models import Sum, Count
from .forms import *
from .views import *
from django.views.decorators.cache import never_cache
import csv
import xlwt
from datetime import datetime


# ..........showing sales report...............
@never_cache
def sales_report(request):
    if request.session.has_key('admin'):
        sales = order_placed.objects.values('orderdate__day', 'orderdate__month', 'orderdate__year', 'product__brand').filter(
            status='Delivered').annotate(Count('quantity'), Sum('sub_total'))
        daily_income = order_placed.objects.values('orderdate__day', 'orderdate__month', 'orderdate__year').filter(
            status='Delivered').annotate(Count('quantity'), Sum('sub_total'))
        context = {
            'sales': sales,
            'daily_income': daily_income,
        }
        return render(request, 'dashboard/salesreport.html', context)
    else:
        return redirect('admin_login')


# ...........exporting sales report to csv format..............
@never_cache
def export_to_csv(request):
    if request.session.has_key('admin'):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename=SalesReport' +\
            str(datetime.now())+'.csv'
        writer = csv.writer(response)
        writer.writerow(['Brandname', 'quantitysold', 'date', 'income'])
        sales = order_placed.objects.values('orderdate__day', 'orderdate__month', 'orderdate__year', 'product__brand').filter(
            status='Delivered').annotate(Count('quantity'), Sum('sub_total'))
        data = order_placed.objects.all()
        for sale in data:
            writer.writerow([sale.product, sale.quantity,
                            sale.orderdate, sale.sub_total])
        return response
    else:
        return redirect('admin_login')


# .............getting sales report in excel format.........................
@never_cache
def export_to_excel(request):
    if request.session.has_key('admin'):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment;filename=SalesReport' +\
            str(datetime.now())+'.xls'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('SalesReport')
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        columns = [['Product', 'quantity', 'date', 'income']]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
        font_style = xlwt.XFStyle()
        rows = order_placed.objects.all().values_list(
            'product', 'quantity', 'orderdate', 'sub_total')
        for row in rows:
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, str(row[col_num]), font_style)
        wb.save(response)
        return response
    else:
        return redirect('admin_login')
