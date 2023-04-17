from django.db import connection
import csv

def importFromCSV(file):
    print(file)
    with open('dashboard/static/dashboard/files/upload/'+file.name, 'wb') as destination:  
        for chunk in file.chunks():  
            destination.write(chunk)  


    with open('dashboard/static/dashboard/files/upload/'+file.name, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)

        facility_procedure_data = []
        #[(1, 1, 600, "Average", "Above"), (1, 2, 600, "Average", "Above"), (1, 3, 600, "Average", "Above")]
        rating_data = []

        states = getAllStates()
        facility_types = getAllTypes()

        print(facility_types)

        #((), ())
        #(Example,DEMO,NY,Government,2,Below,Above,Below,Below,Same,Above,Same,23394,Average,Average,17041,Average,Average,18281,Average,Average,25812,Average,Higher)
        for row in reader:
            facility_name = row[0]
            facility_city = row[1]
            facility_state = row[2]
            facility_type = row[3]

            rating_overall = row[4]
            rating_mortality = row[5]
            rating_safety = row[6]
            rating_readmission = row[7]
            rating_experience = row[8]
            rating_effectiveness = row[9]
            rating_timeliness = row[10]
            rating_imaging = row[11]

            heart_attack_cost = row[12]
            heart_attack_quality = row[13]
            heart_attack_value = row[14]

            heart_failure_cost = row[15]
            heart_failure_quality = row[16]
            heart_failure_value = row[17]

            pneumonia_cost = row[18]
            pneumonia_quality = row[19]
            pneumonia_value = row[20]

            hip_knee_cost = row[21]
            hip_knee_quality = row[22]
            hip_knee_value = row[23]

            facility_state_id = get_tuple_value(states, facility_state)
            facility_type_id = get_tuple_value(facility_types, facility_type)

            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO facility (name, city, state_id, type_id) VALUES (%s, %s, %s, %s)", [facility_name, facility_city, facility_state_id, facility_type_id])
                facility_id = cursor.lastrowid
                facility_procedure_data.append((facility_id, 1, heart_attack_cost, heart_attack_quality, heart_attack_value))
                facility_procedure_data.append((facility_id, 2, heart_failure_cost, heart_failure_quality, heart_failure_value))
                facility_procedure_data.append((facility_id, 3, pneumonia_cost, pneumonia_quality, pneumonia_value))
                facility_procedure_data.append((facility_id, 4, hip_knee_cost, hip_knee_quality, hip_knee_value))

                rating_data.append((facility_id, rating_overall, rating_mortality, rating_safety, rating_readmission, rating_experience, rating_effectiveness, rating_timeliness, rating_imaging))

                if len(rating_data) > 500:
                    cursor.executemany("INSERT INTO rating (facility_id, overall, mortality, safety, readmission, experience, effectiveness, timeliness, imaging) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", rating_data)
                    cursor.executemany("INSERT INTO facility_procedures (facility_id, procedure_id, cost, quality, value) VALUES (%s, %s, %s, %s, %s)", facility_procedure_data)
                    facility_procedure_data = []
                    rating_data = []

                if len(rating_data) > 0:
                    cursor.executemany("INSERT INTO rating (facility_id, overall, mortality, safety, readmission, experience, effectiveness, timeliness, imaging) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", rating_data)
                    cursor.executemany("INSERT INTO facility_procedures (facility_id, procedure_id, cost, quality, value) VALUES (%s, %s, %s, %s, %s)", facility_procedure_data)
                    facility_procedure_data = []
                    rating_data = []

#Facility
def createFacility(name, city, state_id, type_id):
    with connection.cursor() as cursor: 
        try:    
            cursor.execute("INSERT INTO facility (name, city, state_id, type_id) VALUES (%s, %s, %s, %s)", [name, city, state_id, type_id])
            return "Successfully created record"
        except:
            return "Failed to insert into db"

def getAllFacilities(search_query, limit, offset):
    with connection.cursor() as cursor:
        if search_query == "":
            cursor.execute("SELECT facility.id, facility.name, facility.city, states.name, type.type FROM ((`facility` INNER JOIN states ON facility.state_id = states.id) INNER JOIN type ON facility.type_id = type.id) ORDER BY facility.id DESC LIMIT %s OFFSET %s;", [limit, offset])
            rows = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) FROM facility")
            item_count = cursor.fetchone()[0]
            if len(rows) < limit:
                has_next_page = False
            else:
                has_next_page = True 
            return rows, has_next_page, item_count
        
        search_query = "%" + search_query + "%"
        cursor.execute("SELECT facility.id, facility.name, facility.city, states.name, type.type FROM ((`facility` INNER JOIN states ON facility.state_id = states.id) INNER JOIN type ON facility.type_id = type.id) WHERE (facility.name LIKE %s) OR (facility.city LIKE %s) OR (states.name LIKE %s) ORDER BY facility.id LIMIT %s OFFSET %s;", [search_query, search_query, search_query, limit, offset])
        rows = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) FROM ((`facility` INNER JOIN states ON facility.state_id = states.id) INNER JOIN type ON facility.type_id = type.id) WHERE (facility.name LIKE %s) OR (facility.city LIKE %s) OR (states.name LIKE %s)", [search_query, search_query, search_query])
        item_count = cursor.fetchone()[0]
        if len(rows) < limit:
            has_next_page = False
        else:
            has_next_page = True 
        return rows, has_next_page, item_count

def getSingleFacility(facility_id):
    with connection.cursor() as cursor: 
        cursor.execute("SELECT facility.id, facility.name, facility.city, facility.state_id, facility.type_id, states.name, type.type FROM ((`facility` INNER JOIN states ON facility.state_id = states.id) INNER JOIN type ON facility.type_id = type.id) WHERE facility.id = %s;", [facility_id])
        result = cursor.fetchone()

    return result

def updateSingleFacility(name, city, state_id, type_id, facility_id):
    with connection.cursor() as cursor:
        try: 
            cursor.execute("UPDATE facility SET facility.name = %s, facility.city = %s, facility.state_id = %s, facility.type_id = %s WHERE facility.id = %s;", [name, city, state_id, type_id, facility_id])
            return "Succesfully updated facility!"
        except:
            return "Failed to update facility :("

def deleteSingleFacility(facility_id):
    with connection.cursor() as cursor: 
        cursor.execute("DELETE FROM facility_procedures WHERE facility_procedures.facility_id = %s;", [facility_id])
        cursor.execute("DELETE FROM rating WHERE rating.facility_id = %s;", [facility_id])
        cursor.execute("DELETE FROM facility WHERE facility.id = %s;", [facility_id])

#Procedures
def createProcedure(name):
    with connection.cursor() as cursor:
        try:
            cursor.execute("INSERT INTO procedures (name) VALUES (%s)", [name])
            return "Succesfully created new procedure"
        except:
            return "Failed to create new procedure :("

def getAllProcedures(search_query, limit, offset):
    with connection.cursor() as cursor: 
        if search_query == "":
            cursor.execute("SELECT * FROM procedures ORDER BY procedures.id LIMIT %s OFFSET %s", [limit, offset])
            rows = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) FROM procedures")
            item_count = cursor.fetchone()[0]
            if len(rows) < limit:
                has_next_page = False
            else:
                has_next_page = True 
            return rows, has_next_page, item_count
        
        search_query = "%" + search_query + "%"
        cursor.execute("SELECT * FROM procedures WHERE procedures.name LIKE %s ORDER BY procedures.id LIMIT %s OFFSET %s", [search_query, limit, offset])
        rows = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) FROM procedures WHERE procedures.name LIKE %s", [search_query])
        item_count = cursor.fetchone()[0]
        if len(rows) < limit:
                has_next_page = False
        else:
            has_next_page = True 
        return rows, has_next_page, item_count
    
def getSingleProcedure(procedure_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM procedures WHERE procedures.id = %s", [procedure_id])
        row = cursor.fetchone()
        return row
    
def updateSingleProcedure(procedure_id, name):
    with connection.cursor() as cursor:
        try:
            print(name)
            cursor.execute("UPDATE procedures SET procedures.name = %s WHERE procedures.id = %s;", [name, procedure_id])
            return "Succesfully updated procedure!"
        except:
            return "Failed to update procedure :("
        
def deleteSingleProcedure(procedure_id):
    with connection.cursor() as cursor:
        try:
            cursor.execute("DELETE FROM facility_procedures WHERE facility_procedures.procedure_id = %s;", [procedure_id])
            cursor.execute("DELETE FROM procedures WHERE procedures.id = %s;", [procedure_id])
            return "Succesfully deleted procedure!"
        except:
            return "Failed to delete procedure :("
        
#Ratings
def addFacilityRating(facility_id, overall, mortality, safety, readmission, experience, effectiveness, timeliness, imaging):
    with connection.cursor() as cursor:
        try:
            cursor.execute("INSERT INTO rating (facility_id, overall, mortality, safety, readmission, experience, effectiveness, timeliness, imaging) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", [facility_id, overall, mortality, safety, readmission, experience, effectiveness, timeliness, imaging])
            return "Succesfully rated facility"
        except:
            return "Failed to rate facility"

def getAllRatings(search_query, limit, offset):
    with connection.cursor() as cursor:
        if search_query == "":
            cursor.execute("SELECT facility.id, facility.name, facility.city, rating.* FROM rating INNER JOIN facility ON facility.id = rating.facility_id LIMIT %s OFFSET %s;", [limit, offset])
            rows = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) FROM rating")
            item_count = cursor.fetchone()[0]
            if len(rows) < limit:
                has_next_page = False
            else:
                has_next_page = True 
            return rows, has_next_page, item_count
        
        search_query = '%' + search_query + '%'
        cursor.execute("SELECT facility.id, facility.name, facility.city, rating.* FROM rating INNER JOIN facility ON facility.id = rating.facility_id WHERE facility.name LIKE %s LIMIT %s OFFSET %s;", [search_query, limit, offset])
        rows = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) FROM rating INNER JOIN facility ON rating.facility_id = facility.id WHERE facility.name LIKE %s", [search_query])
        item_count = cursor.fetchone()[0]
        if len(rows) < limit:
            has_next_page = False
        else:
            has_next_page = True 
        return rows, has_next_page, item_count

def getAllFacilitiesWithNoRating(search_query, limit, offset):
    with connection.cursor() as cursor:
        if search_query == "":
            cursor.execute("SELECT facility.id, facility.name, facility.city, states.name as state_name, type.type FROM facility INNER JOIN states ON facility.state_id = states.id INNER JOIN type ON facility.type_id = type.id WHERE NOT EXISTS (SELECT facility.id, rating.facility_id FROM rating WHERE rating.facility_id = facility.id) ORDER BY facility.id LIMIT %s OFFSET %s;", [limit, offset])
            rows = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) FROM facility WHERE NOT EXISTS (SELECT facility.id, rating.facility_id FROM rating WHERE rating.facility_id = facility.id)")
            item_count = cursor.fetchone()[0]
            if len(rows) < limit:
                has_next_page = False
            else:
                has_next_page = True 
            return rows, has_next_page, item_count
        
        search_query = '%' + search_query + '%'
        cursor.execute("SELECT facility.id, facility.name, facility.city, states.name as state_name, type.type FROM facility INNER JOIN states ON facility.state_id = states.id INNER JOIN type ON facility.type_id = type.id WHERE (NOT EXISTS (SELECT facility.id, rating.facility_id FROM rating WHERE rating.facility_id = facility.id)) AND (facility.name LIKE %s OR facility.city LIKE %s OR states.name LIKE %s OR type.type LIKE %s) ORDER BY facility.id LIMIT %s OFFSET %s;", [search_query, search_query, search_query, search_query, limit, offset])
        rows = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) FROM facility INNER JOIN states ON facility.state_id = states.id INNER JOIN type ON facility.type_id = type.id WHERE (NOT EXISTS (SELECT facility.id, rating.facility_id FROM rating WHERE rating.facility_id = facility.id)) AND (facility.name LIKE %s OR facility.city LIKE %s OR states.name LIKE %s OR type.type LIKE %s)", [search_query, search_query, search_query, search_query])
        item_count = cursor.fetchone()[0]
        if len(rows) < limit:
            has_next_page = False
        else:
            has_next_page = True 
        return rows, has_next_page, item_count

def getSingleFacilityRating(facility_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT facility.name, rating.* FROM rating INNER JOIN facility ON facility.id = rating.facility_id WHERE rating.facility_id = %s;", [facility_id])
        row = cursor.fetchone()
        return row

def updateSingleFacilityRating(facility_id, overall, mortality, safety, readmission, experience, effectiveness, timeliness, imaging):
    with connection.cursor() as cursor:
        try:
            cursor.execute("UPDATE rating SET overall = %s, mortality = %s, safety = %s, readmission = %s, experience = %s, effectiveness = %s, timeliness = %s, imaging = %s WHERE rating.facility_id = %s;", [overall, mortality, safety, readmission, experience, effectiveness, timeliness, imaging, facility_id])
            return "Succesfully updated facility rating"
        except:
            return "Failed to update facility rating :("

def deleteSingleFacilityRating(facility_id):
    with connection.cursor() as cursor:
        try:
            cursor.execute("DELETE FROM rating WHERE rating.facility_id = %s;", [facility_id])
            return "Succesfully deleted facility rating"
        except:
            return "Failed to delete facility rating"

#Facility Procedures
def getAllFacilityProcedures(search_query, limit, offset):
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM procedures")
        procedure_amount = cursor.fetchone()[0]
        limit = limit * procedure_amount;

        if search_query == "":
            cursor.execute("SELECT facility.id as facility_id, facility.name, facility.city, states.name AS state_name, facility_procedures.cost, facility_procedures.procedure_id, procedures.name AS procedure_name, facility_procedures.quality, facility_procedures.value FROM facility_procedures INNER JOIN facility ON facility.id = facility_procedures.facility_id INNER JOIN procedures ON procedures.id = facility_procedures.procedure_id INNER JOIN states ON facility.state_id = states.id ORDER BY facility.id, facility_procedures.procedure_id LIMIT %s OFFSET %s;", [limit, offset])
            rows = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) FROM facility_procedures INNER JOIN facility ON facility.id = facility_procedures.facility_id")
            item_count = cursor.fetchone()[0]
            if len(rows) < limit:
                has_next_page = False
            else:
                has_next_page = True 
            return rows, has_next_page, item_count
        
        search_query = '%' + search_query + '%'
        cursor.execute("SELECT facility.id as facility_id, facility.name, facility.city, states.name AS state_name, facility_procedures.cost, facility_procedures.procedure_id, procedures.name AS procedure_name, facility_procedures.quality, facility_procedures.value FROM facility_procedures INNER JOIN facility ON facility.id = facility_procedures.facility_id INNER JOIN procedures ON procedures.id = facility_procedures.procedure_id INNER JOIN states ON facility.state_id = states.id WHERE facility.name LIKE %s OR facility.city LIKE %s OR states.name LIKE %s ORDER BY facility.id, facility_procedures.procedure_id LIMIT %s OFFSET %s;", [search_query, search_query, search_query, limit, offset])
        rows = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) FROM facility_procedures INNER JOIN facility ON facility.id = facility_procedures.facility_id WHERE facility.name LIKE %s OR facility.city LIKE %s", [search_query, search_query])
        item_count = cursor.fetchone()[0]
        if len(rows) < limit:
            has_next_page = False
        else:
            has_next_page = True 
        return rows, has_next_page, item_count
    
def getSingleProcedureFacilities(search_query, limit, offset, procedure_id):
    with connection.cursor() as cursor:
        if search_query == "":
            cursor.execute("SELECT facility.id AS facility_id, facility.name AS facility_name, facility.city, states.name AS state, type.type, procedures.id AS procedure_id, procedures.name AS procedure_name, facility_procedures.cost, facility_procedures.quality, facility_procedures.value FROM facility_procedures INNER JOIN facility ON facility.id = facility_procedures.facility_id INNER JOIN states ON states.id = facility.state_id INNER JOIN type ON type.id = facility.type_id INNER JOIN procedures ON procedures.id = facility_procedures.procedure_id WHERE procedures.id = %s LIMIT %s OFFSET %s;", [procedure_id, limit, offset])
            rows = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) FROM facility_procedures INNER JOIN facility ON facility.id = facility_procedures.facility_id INNER JOIN procedures ON procedures.id = facility_procedures.procedure_id WHERE procedures.id = %s", [procedure_id])
            item_count = cursor.fetchone()[0]
            if len(rows) < limit:
                has_next_page = False
            else:
                has_next_page = True 
            return rows, has_next_page, item_count  
            
        search_query = '%' + search_query + '%'
        cursor.execute("SELECT facility.id AS facility_id, facility.name AS facility_name, facility.city, states.name AS state, type.type, procedures.id AS procedure_id, procedures.name AS procedure_name, facility_procedures.cost, facility_procedures.quality, facility_procedures.value FROM facility_procedures INNER JOIN facility ON facility.id = facility_procedures.facility_id INNER JOIN states ON states.id = facility.state_id INNER JOIN type ON type.id = facility.type_id INNER JOIN procedures ON procedures.id = facility_procedures.procedure_id WHERE procedures.id = %s AND ( facility.name LIKE %s OR facility.city LIKE %s OR states.name LIKE %s) LIMIT %s OFFSET %s;", [procedure_id, search_query, search_query, search_query, limit, offset])
        rows = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) FROM facility_procedures INNER JOIN facility ON facility.id = facility_procedures.facility_id INNER JOIN procedures ON procedures.id = facility_procedures.procedure_id INNER JOIN states ON facility.state_id = states.id WHERE procedures.id = %s AND (facility.name LIKE %s OR facility.city LIKE %s OR states.name LIKE %s)", [procedure_id, search_query, search_query, search_query])
        item_count = cursor.fetchone()[0]
        if len(rows) < limit:
            has_next_page = False
        else:
            has_next_page = True 
        return rows, has_next_page, item_count

def getAllFacilitiesWithNoProcedures(search_query, limit, offset):
    with connection.cursor() as cursor:
        if search_query == "":
            cursor.execute("SELECT facility.id, facility.name, facility.city, states.name as state_name, type.type FROM facility INNER JOIN states ON facility.state_id = states.id INNER JOIN type ON facility.type_id = type.id WHERE NOT EXISTS (SELECT facility.id, facility_procedures.facility_id FROM facility_procedures WHERE facility_procedures.facility_id = facility.id) ORDER BY facility.id LIMIT %s OFFSET %s;", [limit, offset])
            rows = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) FROM facility WHERE NOT EXISTS (SELECT facility.id, facility_procedures.facility_id FROM facility_procedures WHERE facility_procedures.facility_id = facility.id)")
            item_count = cursor.fetchone()[0]
            if len(rows) < limit:
                has_next_page = False
            else:
                has_next_page = True 
            return rows, has_next_page, item_count
        
        search_query = '%' + search_query + '%'
        cursor.execute("SELECT facility.id, facility.name, facility.city, states.name as state_name, type.type FROM facility INNER JOIN states ON facility.state_id = states.id INNER JOIN type ON facility.type_id = type.id WHERE (NOT EXISTS (SELECT facility.id, facility_procedures.facility_id FROM facility_procedures WHERE facility_procedures.facility_id = facility.id)) AND (facility.name LIKE '%s' OR facility.city LIKE '%s' OR states.name LIKE '%s' OR type.type LIKE '%s') ORDER BY facility.id LIMIT %s OFFSET %s;", [search_query, search_query, search_query, search_query, limit, offset])
        rows = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) FROM facility INNER JOIN states ON facility.state_id = states.id INNER JOIN type ON facility.type_id = type.id WHERE (NOT EXISTS (SELECT facility.id, facility_procedures.facility_id FROM facility_procedures WHERE facility_procedures.facility_id = facility.id)) AND (facility.name LIKE '%s' OR facility.city LIKE '%s' OR states.name LIKE '%s' OR type.type LIKE '%s')", [search_query, search_query, search_query, search_query])
        item_count = cursor.fetchone()[0]
        if len(rows) < limit:
            has_next_page = False
        else:
            has_next_page = True 
        return rows, has_next_page, item_count    
    
def getSingleFacilityProcedures(facility_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT facility.id AS facility_id, facility.name AS facility_name, facility.city, states.name AS state, type.type, procedures.id AS procedure_id, procedures.name AS procedure_name, facility_procedures.cost, facility_procedures.quality, facility_procedures.value FROM facility_procedures INNER JOIN facility ON facility.id = facility_procedures.facility_id INNER JOIN states ON states.id = facility.state_id INNER JOIN type ON type.id = facility.type_id INNER JOIN procedures ON procedures.id = facility_procedures.procedure_id WHERE facility.id = %s;", [facility_id])
        rows = cursor.fetchall()
        return rows;

def addSingleFacilityProcedures(facility_id, data: list):
    with connection.cursor() as cursor:
        try:
            for procedure_id, procedure in enumerate(data, start=1):
                cost = procedure[0]
                quality = procedure[1]
                value = procedure[2]
                cursor.execute("INSERT INTO facility_procedures VALUES (%s, %s, %s, %s, %s)", [facility_id, procedure_id, cost, quality, value ])
            return
        except:
            return;

def getSingleProcedureFacility(facility_id, procedure_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT facility.id AS facility_id, facility.name AS facility_name, facility.city, states.name AS state, type.type, procedures.id AS procedure_id, procedures.name AS procedure_name, facility_procedures.cost, facility_procedures.quality, facility_procedures.value FROM facility_procedures INNER JOIN facility ON facility.id = facility_procedures.facility_id INNER JOIN states ON states.id = facility.state_id INNER JOIN type ON type.id = facility.type_id INNER JOIN procedures ON procedures.id = facility_procedures.procedure_id WHERE facility_procedures.facility_id = %s AND facility_procedures.procedure_id = %s;", [facility_id, procedure_id])
        row = cursor.fetchall()
        return row
    
def editSingleFacilityProcedures(facility_id, data: list):
    with connection.cursor() as cursor:
        for procedure_id, procedure in enumerate(data):
            cost = procedure[0]
            quality = procedure[1]
            value = procedure[2]
            cursor.execute("UPDATE facility_procedures SET facility_procedures.cost = %s, facility_procedures.quality = %s, facility_procedures.value = %s WHERE facility_procedures.facility_id = %s AND facility_procedures.procedure_id = %s", [cost, quality, value, facility_id, procedure_id + 1])
        return

def editSingleProcedureFacility(facility_id, procedure_id, cost, quality, value):
    with connection.cursor() as cursor:
        try:
            cursor.execute("UPDATE facility_procedures SET facility_procedures.cost = %s, facility_procedures.quality = %s, facility_procedures.value = %s WHERE facility_procedures.facility_id = %s AND facility_procedures.procedure_id = %s", [cost, quality, value, facility_id, procedure_id])
            return "Successfully updated"
        except:
            return "Failed to update"

def deleteSingleFacilityProcedures(facility_id):
     with connection.cursor() as cursor:
        try:
            cursor.execute("DELETE FROM facility_procedures WHERE facility_procedures.facility_id = %s;", [facility_id])
            return "Succesfully deleted facility procedures"
        except:
            return "Failed to delete facility prpcedures"

#Reports

def getFacilitiesWithSameSafetyRating():
    with connection.cursor() as cursor:
        cursor.execute("SELECT facility.id, facility.name, facility.city, states.name AS state_name, type.type, rating.overall, rating.safety, rating.mortality FROM rating INNER JOIN facility ON facility.id = rating.facility_id INNER JOIN states ON states.id = facility.state_id INNER JOIN type ON facility.type_id = type.id WHERE rating.safety = 'Same';")
        return cursor.fetchall()
    
def getFacilitiesWithAverageHeartAttackQuality():
    with connection.cursor() as cursor:
        cursor.execute("SELECT facility.id, facility.name, facility.city, states.name AS state_name, type.type, facility_procedures.cost, facility_procedures.quality, facility_procedures.value, rating.overall FROM facility_procedures INNER JOIN facility ON facility.id = facility_procedures.facility_id INNER JOIN states ON states.id = facility.state_id INNER JOIN type ON type.id = facility.type_id INNER JOIN rating ON rating.facility_id = facility.id WHERE facility_procedures.procedure_id = 1 AND facility_procedures.quality = 'Average';")
        return cursor.fetchall()
    
def getFacilitiesWithZeroHipKneeCost():
    with connection.cursor() as cursor:
        cursor.execute("SELECT facility.id, facility.name, facility.city, states.name AS state_name, type.type, facility_procedures.cost, facility_procedures.quality, facility_procedures.value, rating.overall FROM facility_procedures INNER JOIN facility ON facility.id = facility_procedures.facility_id INNER JOIN states ON states.id = facility.state_id INNER JOIN type ON type.id = facility.type_id INNER JOIN rating ON rating.facility_id = facility.id WHERE facility_procedures.procedure_id = 4 AND facility_procedures.cost = 0;")
        return cursor.fetchall()
    
#Miscellanous

def getAllTypes():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM type")
        row = cursor.fetchall()

    return row

def getProcedureCount():
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) from procedures")
        count = cursor.fetchone()[0]
        return count

def getAllStates():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM states")
        row = cursor.fetchall()

    return row

def get_tuple_value(t, value):
    for e in t:
        if e[1] == value:
            return e[0]

