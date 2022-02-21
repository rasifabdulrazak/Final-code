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
        report = order_placed.objects.all()
        context = {
            'sales': sales,
            'daily_income': daily_income,
            'report':report,
        }
        return render(request, 'dashboard/salesreport.html', context)
    else:
        return redirect('admin_login')



@never_cache
def month_report(request):
    if request.session.has_key('admin'):
        if request.method == "POST":
            month_report = request.POST['month']
            print(month_report)
            if month_report!='':
                month = month_report.split('-')
                report = order_placed.objects.filter(orderdate__month = month[1],orderdate__year = month[0]).order_by('-orderdate')
            else:
                report = order_placed.objects.all().order_by('-orderdate')
            return render(request, 'dashboard/salesreport.html',{'report':report})
    else:
        return redirect('admin_login')


@never_cache
def year_report(request):
    if request.session.has_key('admin'):
        if request.method == "POST":
            year = int(request.POST['year'])
            if year!='':
                report = order_placed.objects.filter(orderdate__year = year).order_by('-orderdate')
            else:
                report = order_placed.objects.all().order_by('-orderdate')
            return render(request, 'dashboard/salesreport.html',{'report':report})
    else:
        return redirect('admin_login')



# For searching sales based on date
@never_cache
def daily_report(request):
    if request.session.has_key('admin'):
        if request.method == 'POST':
            fromdate = request.POST['from']
            to = request.POST['to']
            if to != '':
                setto = to.split('-')
                if (int(setto[2])+1) < 10:
                    setto[2] = '0'+str(int(setto[2])+1)
                else:
                    setto[2] = str(int(setto[2])+1)
                todate = '-'.join(setto)
            else:
                todate = ''
            request.session['fromdate'] = fromdate
            request.session['todate'] = todate
            if fromdate == '' and todate == '':
                report = order_placed.objects.all().order_by('-orderdate')
            elif fromdate == '':
                report = order_placed.objects.filter(orderdate__lt=todate).order_by('-orderdate')
            elif todate == '':
                report = order_placed.objects.filter(
                    orderdate__gte=fromdate).order_by('-orderdate')
            else:
                report = order_placed.objects.filter(
                    orderdate__range=[fromdate, todate]).order_by('-orderdate')
            return render(request, 'dashboard/salesreport.html', {'report': report})
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
