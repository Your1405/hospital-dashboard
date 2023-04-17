from django.urls import path

from . import views

app_name = 'dashboard'
urlpatterns = [
    # /dashboard
    path('', views.index, name="index"),
    path('overviews/', views.viewOverviewScreen, name="overviewTemplate"),

    path('overviews/facilities', views.viewFacilities, name="overzichtFacility"),
    path('overviews/facilities/new', views.newFacility, name="newFacility"),
    path('overviews/facilities/<int:facility_id>', views.viewSingleFacility, name="viewFacility"),
    path('overviews/facilities/edit/<int:facility_id>', views.updateFacility, name="updateFacility"),
    path('overviews/facilities/delete/<int:facility_id>', views.deleteFacility, name="deleteFacility"),

    path('overviews/procedures', views.viewProcedures, name="overzichtProcedures"),
    path('overviews/procedures/new', views.newProcedure, name="newProcedure"),
    path('overviews/procedures/<int:procedure_id>', views.viewSingleProcedure, name="viewProcedure"),
    path('overviews/procedures/edit/<int:procedure_id>', views.updateProcedure, name="updateProcedure"),
    path('overviews/procedures/delete/<int:procedure_id>', views.deleteProcedure, name="deleteProcedure"),

    path('overviews/ratings/all', views.viewAllRatings, name="overzichtAllFacilities"),
    path('overviews/ratings/none', views.viewNoRatings, name="overzichtNonRatedFacilities"),
    path('overviews/ratings/add/<int:facility_id>', views.newRating, name="addRating"),
    path('overviews/ratings/<int:facility_id>', views.viewSingleFacilityRating, name="viewFacilityRating"),
    path('overviews/ratings/edit/<int:facility_id>', views.updateRating, name="updateFacilityRating"),
    path('overviews/ratings/delete/<int:facility_id>', views.deleteRating, name="deleteFacilityRating"),

    path('overviews/facilityprocedures/all', views.viewAllFacilityProcedures, name="overzichtAllFacilityProcedures"),
    path('overviews/facilityprocedures/none', views.viewAllFacilitiesWithNoProcedures, name="overzichtNonProcedureFacilities"),
    path('overviews/facilityprocedures/<int:procedure>', views.viewSingleProcedureFacilities, name="singleFacilityProcedures"),
    path('overviews/facilityprocedures/facility/add/<int:facility_id>', views.newSingleFacilityProcedures, name="addSingleFacilityProcedures"),
    path('overviews/facilityprocedures/facility/<int:facility_id>', views.viewSingleFacilityProcedures, name="viewFacilityProcedures"),
    path('overviews/facilityprocedures/facility/edit/<int:facility_id>', views.updateSingleFacilityProcedures, name="updateFacilityProcedures"),
    path('overviews/facilityprocedures/facility/delete/<int:facility_id>', views.removeSingleFacilityProcedures, name="deleteFacilityProcedures"),

    path('import/', views.viewImportScreen, name="importTemplate"),
    path('import/success', views.importSuccess, name="importSucces"),
    path('import/download', views.downloadCSVTemplate, name="downloadTemplate"),
    path('export', views.viewExportScreen, name="exportTemplate"),
]
