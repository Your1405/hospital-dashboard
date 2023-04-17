import math
import os
from django.shortcuts import render
from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseRedirect
from .utils import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A3
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

# Create your views here.
def index(request):
    return render(request, 'dashboard/dashboard.html')

def viewImportScreen(request):
    if request.method == "POST":
        importFromCSV(request.FILES["file"])
        return HttpResponseRedirect('/dashboard/import/success')
    
    return render(request, 'dashboard/import.html')

def importSuccess(request):
    return render(request, "dashboard/import-success.html")

def downloadCSVTemplate(request):
    file_path = 'dashboard/static/dashboard/files/hospitals_template.csv'
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/csv")
            response['Content-Disposition'] = 'inline; filename=hospitals_template.csv'
            return response
    raise Http404()

def viewOverviewScreen(request):
    return render(request, 'dashboard/overview.html')

def viewFacilities(request):
    if request.method == 'POST':
        search_params = request.POST.get('search', '')
        page = str(request.GET.get('page', 1))
        return HttpResponseRedirect("/dashboard/overviews/facilities?search=" + search_params + "&page=" + page)
    
    search_params = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    if page < 1:
        page = 1
    limit = 10
    offset = (page - 1) * limit
    data = getAllFacilities(search_params, limit, offset)
    facilities = data[0]
    item_count = data[2]
    
    total_pages = math.ceil(item_count / limit)

    return render(request, 'dashboard/overviews/facility/index.html', {
        "facilities": facilities, 
        "search_query": search_params, 
        "current_page": page,
        "pages": range(1, total_pages + 1),
        "total_pages": total_pages, 
        "has_next_page": data[1]
    })

def newFacility(request):
    if request.method == 'POST':
        post_data = request.POST
        result = createFacility(post_data.get("name"), post_data.get("city"), post_data.get("state"), post_data.get("type"))
        return HttpResponseRedirect("/dashboard/overviews/facilities")

    states = getAllStates()
    types = getAllTypes()
    message = ""
    data = {"states": states, "types": types, "messages": message}
    return render(request, 'dashboard/overviews/facility/new.html', data)

def viewSingleFacility(request, facility_id):
    facility_data = getSingleFacility(facility_id)
    rating_data = getSingleFacilityRating(facility_id)
    facility_procedures = getSingleFacilityProcedures(facility_id)
    data = {
        'rating_data': rating_data,
        'facility_data': facility_data,
        'facility_procedures': facility_procedures,
        'id': facility_id
    }
    return render(request, 'dashboard/overviews/facility/view.html', data)

def updateFacility(request, facility_id):
    if request.method == 'POST':
        data = request.POST
        message = updateSingleFacility(data.get("name"), data.get("city"), data.get("state"), data.get("type"), facility_id)
        return HttpResponseRedirect('/dashboard/overviews/facilities/' + str(facility_id));

    data = {
        'facility_data': getSingleFacility(facility_id),
        'states': getAllStates(),
        'types': getAllTypes(),
        'id': facility_id
    }
    return render(request, 'dashboard/overviews/facility/update.html', data)

def deleteFacility(request, facility_id):
    if request.method == "POST":
        choice = request.POST.get("choice")
        if choice == "yes":
            deleteSingleFacility(facility_id)
            return HttpResponseRedirect('/dashboard/overviews/facilities')
        else:
            return HttpResponseRedirect('/dashboard/overviews/facilities/' + str(facility_id))

    facility = getSingleFacility(facility_id)

    data = {
        'facility_data': facility,
        'id': facility_id
    }

    return render(request, 'dashboard/overviews/facility/delete.html', data)

def viewProcedures(request):
    if request.method == 'POST':
        search_params = request.POST.get('search', '')
        page = str(request.GET.get('page', 1))
        return HttpResponseRedirect("/dashboard/overviews/procedures?search=" + search_params + "&page=" + page)
    
    search_params = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    if page < 1:
        page = 1
    limit = 10
    offset = (page - 1) * limit
    data = getAllProcedures(search_params, limit, offset)
    procedures = data[0]
    item_count = data[2]
    
    total_pages = math.ceil(item_count / limit)

    return render(request, 'dashboard/overviews/procedure/index.html', {
        "procedures": procedures, 
        "search_query": search_params, 
        "current_page": page,
        "pages": range(1, total_pages + 1),
        "total_pages": total_pages, 
        "has_next_page": data[1]
    })

def newProcedure(request):
    if request.method == 'POST':
        post_data = request.POST
        createProcedure(post_data.get("name"))
        return HttpResponseRedirect("/dashboard/overviews/procedures")

    return render(request, 'dashboard/overviews/procedure/new.html')

def viewSingleProcedure(request, procedure_id):
    procedure_data = getSingleProcedure(procedure_id)
    data = {
        'procedure_data': procedure_data,
        'id': procedure_id
    }
    return render(request, 'dashboard/overviews/procedure/view.html', data)

def updateProcedure(request, procedure_id):
    if request.method == 'POST':
        data = request.POST
        updateSingleProcedure(procedure_id, data.get("name"))
        return HttpResponseRedirect('/dashboard/overviews/procedures/' + str(procedure_id))

    data = {
        'procedure_data': getSingleProcedure(procedure_id),
        'id': procedure_id
    }
    return render(request, 'dashboard/overviews/procedure/update.html', data)

def deleteProcedure(request, procedure_id):
    if request.method == "POST":
        choice = request.POST.get("choice")
        if choice == "yes":
            deleteSingleProcedure(procedure_id)
            return HttpResponseRedirect('/dashboard/overviews/procedures')
        else:
            return HttpResponseRedirect('/dashboard/overviews/procedures/' + str(procedure_id))

    procedure = getSingleProcedure(procedure_id)

    data = {
        'procedure_data': procedure,
        'id': procedure_id
    }

    return render(request, 'dashboard/overviews/procedure/delete.html', data)

def viewAllRatings(request):
    if request.method == 'POST':
        search_params = request.POST.get('search', '')
        page = str(request.GET.get('page', 1))
        return HttpResponseRedirect("/dashboard/overviews/ratings/all?search=" + search_params + "&page=" + page)
    
    search_params = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    if page < 1:
        page = 1
    limit = 10
    offset = (page - 1) * limit
    data = getAllRatings(search_params, limit, offset)
    ratings = data[0]
    item_count = data[2]
    
    total_pages = math.ceil(item_count / limit)

    return render(request, 'dashboard/overviews/ratings/all.html', {
        "ratings": ratings, 
        "search_query": search_params, 
        "current_page": page,
        "pages": range(1, total_pages + 1),
        "total_pages": total_pages, 
        "has_next_page": data[1]
    })
    
def viewNoRatings(request):
    if request.method == 'POST':
        search_params = request.POST.get('search', '')
        page = str(request.GET.get('page', 1))
        return HttpResponseRedirect("/dashboard/overviews/ratings/none?search=" + search_params + "&page=" + page)
    
    search_params = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    if page < 1:
        page = 1
    limit = 10
    offset = (page - 1) * limit
    data = getAllFacilitiesWithNoRating(search_params, limit, offset)
    ratings = data[0]
    item_count = data[2]
    
    total_pages = math.ceil(item_count / limit)

    return render(request, 'dashboard/overviews/ratings/none.html', {
        "ratings": ratings, 
        "search_query": search_params, 
        "current_page": page,
        "pages": range(1, total_pages + 1),
        "total_pages": total_pages, 
        "has_next_page": data[1]
    })

def newRating(request, facility_id):
    if request.method == 'POST':
        post_data = request.POST
        addFacilityRating(facility_id, post_data.get("overall"), post_data.get("mortality"), post_data.get("safety"), post_data.get("readmission"), post_data.get("experience"), post_data.get("effectiveness"), post_data.get("timeliness"), post_data.get("imaging"))
        return HttpResponseRedirect("/dashboard/overviews/ratings/" + str(facility_id))

    facility_data = getSingleFacility(facility_id)
    data = {
        "facility_data": facility_data,
        'id': facility_id,
        'rating_choices': ('Below', 'Same', 'Above')
    }
    return render(request, 'dashboard/overviews/ratings/new.html', data)

def viewSingleFacilityRating(request, facility_id):
    rating_data = getSingleFacilityRating(facility_id)
    facility_data = getSingleFacility(facility_id)
    data = {
        'facility_data': facility_data,
        'rating_data': rating_data,
        'overall_rating': range(1, 6),
        'id': facility_id
    }
    return render(request, 'dashboard/overviews/ratings/view.html', data)

def updateRating(request, facility_id):
    if request.method == 'POST':
        post_data = request.POST
        updateSingleFacilityRating(facility_id, post_data.get("overall"), post_data.get("mortality"), post_data.get("safety"), post_data.get("readmission"), post_data.get("experience"), post_data.get("effectiveness"), post_data.get("timeliness"), post_data.get("imaging"))

        return HttpResponseRedirect('/dashboard/overviews/ratings/' + str(facility_id))

    data = {
        'rating_data': getSingleFacilityRating(facility_id),
        'facility_data': getSingleFacility(facility_id),
        'id': facility_id,
        'rating_choices': ('Below', 'Same', 'Above')
    }
    return render(request, 'dashboard/overviews/ratings/update.html', data)

def deleteRating(request, facility_id):
    if request.method == "POST":
        choice = request.POST.get("choice")
        if choice == "yes":
            deleteSingleFacilityRating(facility_id)
            return HttpResponseRedirect('/dashboard/overviews/ratings/none')
        else:
            return HttpResponseRedirect('/dashboard/overviews/ratings/' + str(facility_id))

    facility = getSingleFacility(facility_id)

    data = {
        'facility_data': facility,
        'id': facility_id
    }

    return render(request, 'dashboard/overviews/ratings/delete.html', data)

def viewAllFacilityProcedures(request):
    if request.method == 'POST':
        search_params = request.POST.get('search', '')
        page = str(request.GET.get('page', 1))
        return HttpResponseRedirect("/dashboard/overviews/facilityprocedures/all?search=" + search_params + "&page=" + page)
    
    search_params = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    if page < 1:
        page = 1
    limit = 10
    offset = (page - 1) * limit
    data = getAllFacilityProcedures(search_params, limit, offset)
    procedure_count = getProcedureCount()
    procedures = getAllProcedures('', 1000, 0)
    facility_procedures = []
    single_facility = []
    for facility in data[0]:
        single_facility.append(facility)

        if len(single_facility) == procedure_count:
            facility_procedures.append(single_facility)
            single_facility = []

    item_count = data[2]
    
    total_pages = math.ceil(item_count / limit)

    return render(request, 'dashboard/overviews/facility_procedures/all.html', {
        "facility_procedures": facility_procedures, 
        "procedures": procedures[0],
        "search_query": search_params, 
        "current_page": page,
        "pages": range(1, total_pages + 1),
        "total_pages": total_pages, 
        "has_next_page": data[1]
    })

def viewSingleProcedureFacilities(request, procedure):
    if request.method == 'POST':
        search_params = request.POST.get('search', '')
        page = str(request.GET.get('page', 1))
        return HttpResponseRedirect("/dashboard/overviews/facilityprocedures/" + str(procedure) + "?search=" + search_params + "&page=" + page)
    
    search_params = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    if page < 1:
        page = 1
    limit = 10
    offset = (page - 1) * limit
    data = getSingleProcedureFacilities(search_params, limit, offset, procedure)
    procedure = getSingleProcedure(procedure)
    procedures = getAllProcedures('', 1000, 0)
            
    item_count = data[2]
    
    total_pages = math.ceil(item_count / limit)

    return render(request, 'dashboard/overviews/facility_procedures/procedure.html', {
        "facility_procedures": data[0],
        "procedure_info": procedure, 
        "procedures": procedures[0],
        "search_query": search_params, 
        "current_page": page,
        "pages": range(1, total_pages + 1),
        "total_pages": total_pages, 
        "has_next_page": data[1]
    })

def viewAllFacilitiesWithNoProcedures(request):
    if request.method == 'POST':
        search_params = request.POST.get('search', '')
        page = str(request.GET.get('page', 1))
        return HttpResponseRedirect("/dashboard/overviews/facilityprocedures/none?search=" + search_params + "&page=" + page)
    
    search_params = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    if page < 1:
        page = 1
    limit = 10
    offset = (page - 1) * limit
    data = getAllFacilitiesWithNoProcedures(search_params, limit, offset)
            
    item_count = data[2]
    
    total_pages = math.ceil(item_count / limit)

    return render(request, 'dashboard/overviews/facility_procedures/none.html', {
        "facilities": data[0], 
        "search_query": search_params, 
        "current_page": page,
        "pages": range(1, total_pages + 1),
        "total_pages": total_pages, 
        "has_next_page": data[1]
    })

def viewSingleFacilityProcedures(request, facility_id):
    facility_procedure = getSingleFacilityProcedures(facility_id)
    data = {
        'facility': facility_procedure,
    }
    return render(request, 'dashboard/overviews/facility_procedures/view.html', data)

def newSingleFacilityProcedures(request, facility_id):
    procedures = getAllProcedures('', 1000, 0)
    if request.method == 'POST':
        post_data = request.POST
        input_data = []
        for procedure in procedures[0]:
            cost = post_data.get(procedure[1].lower().replace(" ", "") + "-cost")
            quality = post_data.get(procedure[1].lower().replace(" ", "") + "-quality")
            value = post_data.get(procedure[1].lower().replace(" ", "") + "-value")
            input_data.append([cost, quality, value])

        addSingleFacilityProcedures(facility_id, input_data)
        return HttpResponseRedirect("/dashboard/overviews/facilityprocedures/facility/" + str(facility_id))

    facility_data = getSingleFacility(facility_id)
    data = {
        "facility_data": facility_data,
        "procedures": procedures[0],
        'id': facility_id,
        'choices': ('Worse', 'Lower', 'Average', 'Higher', 'Unknown')
    }
    return render(request, 'dashboard/overviews/facility_procedures/new.html', data)

def updateSingleFacilityProcedures(request, facility_id):
    procedures = getAllProcedures('', 1000, 0)
    facility_data = getSingleFacilityProcedures(facility_id)
    procedure_id = request.GET.get('procedure', 0)
    if request.method == 'POST':
        if procedure_id != 0:
            post_data = request.POST
            facility_data = getSingleProcedureFacility(facility_id, procedure_id)
            editSingleProcedureFacility(facility_id, procedure_id, post_data.get("cost"), post_data.get("quality"), post_data.get("value"))
            return HttpResponseRedirect('/dashboard/overviews/facilityprocedures/facility/' + str(facility_id))
        else:
            post_data = request.POST
            input_data = []
            for procedure in procedures[0]:
                cost = post_data.get(procedure[1].lower().replace(" ", "") + "-cost")
                quality = post_data.get(procedure[1].lower().replace(" ", "") + "-quality")
                value = post_data.get(procedure[1].lower().replace(" ", "") + "-value")
                input_data.append([cost, quality, value])
            editSingleFacilityProcedures(facility_id, input_data)

        return HttpResponseRedirect('/dashboard/overviews/facilityprocedures/facility/' + str(facility_id))

    if procedure_id == 0:
        data = {
            "facility_data": facility_data,
            "procedures": procedures[0],
            'id': facility_id,
            'choices': ('Worse', 'Lower', 'Average', 'Higher', 'Unknown')
        }
        return render(request, 'dashboard/overviews/facility_procedures/update.html', data)
    else:
        facility_data = getSingleProcedureFacility(facility_id, procedure_id)
        data = {
            "facility_data": facility_data,
            'id': facility_id,
            'procedure_id': procedure_id,
            'choices': ('Worse', 'Lower', 'Average', 'Higher', 'Unknown')
        }
        return render(request, 'dashboard/overviews/facility_procedures/update-procedure.html', data)

def removeSingleFacilityProcedures(request, facility_id):
    if request.method == "POST":
        choice = request.POST.get("choice")
        if choice == "yes":
            deleteSingleFacilityProcedures(facility_id)
            return HttpResponseRedirect('/dashboard/overviews/facilityprocedures/none')
        else:
            return HttpResponseRedirect('/dashboard/overviews/facilityprocedures/facility/' + str(facility_id))

    facility = getSingleFacility(facility_id)

    data = {
        'facility_data': facility,
        'id': facility_id
    }

    return render(request, 'dashboard/overviews/facility_procedures/delete.html', data)

def viewExportScreen(request):
    doc_num = int(request.GET.get("doc", 0))
    if doc_num == 0:
        return render(request, 'dashboard/export.html')
    
    response = HttpResponse(content_type='application/pdf')

    doc = SimpleDocTemplate(response, pagesize=landscape(A3), title="Overview")
    
    data = []
    elements = []
    title = ""

    if doc_num == 1:
        row_data = getFacilitiesWithSameSafetyRating()
        data = [['', 'Facility Name', 'City', 'State', 'Type', 'Overall Rating', 'Safety Rating', 'Mortality Rating'],
            *[[row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]] for row in row_data]]
        title = "Facilities with 'Same' safety rating"
        response['Content-Disposition'] = 'attachment; filename="facilities-with-same-rating.pdf"'
        
    if doc_num == 2:
        row_data = getFacilitiesWithAverageHeartAttackQuality()
        data = [['', 'Facility Name', 'City', 'State', 'Type', 'Heart Attack Cost', 'Heart Attack Quality', 'Heart Attack Value', 'Overall Rating'],
            *[[row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]] for row in row_data]]
        title = "Facilities with 'Average' heart attack quality"
        response['Content-Disposition'] = 'attachment; filename="facilities-with-average-heart-attack-quality.pdf"'
        
    if doc_num == 3:
        row_data = getFacilitiesWithZeroHipKneeCost()
        data = [['', 'Facility Name', 'City', 'State', 'Type', 'Hip Knee Cost', 'Hip Knee Quality', 'Hip Knee Value', 'Overall Rating'],
            *[[row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]] for row in row_data]]
        title = "Facilities with hip knee cost of 0"
        response['Content-Disposition'] = 'attachment; filename="facilities-with-0-hip-knee-cost.pdf"'

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 16),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
    ]))

    title_paragraph = Paragraph(title, getSampleStyleSheet()['Title'])

    elements.append(title_paragraph)
    elements.append(table)
    doc.build(elements)
    return response