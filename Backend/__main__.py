#!/usr/bin/python
# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import tornado.autoreload
import tornado.httpserver
import os
import config
import MySQLdb
db = MySQLdb.connect(config.host, config.user, config.pswd, config.name, autocommit=True)
import json







#       
#
class MainPage(tornado.web.RequestHandler):
	def get(self):
		fileToLoad = self.request.uri.split("?")[0]
		if(self.request.uri == "/"):
			self.render("../Interface/index.html")
		else:
			extension = fileToLoad[-3:]
			if(extension == "css") :
				self.set_header('Content-Type', 'text/css')
			elif(extension == ".js"):
				self.set_header('Content-Type', 'text/javascript')
			elif(extension == "png"):
				self.set_header('Content-Type', 'image/png')
				self.finish(open("../Interface"+fileToLoad, 'rb').read())
				return
			elif(extension == "svg"):
				self.set_header('Content-Type', 'image/svg+xml')
				self.finish(open("../Interface"+fileToLoad, 'rb').read())
				return
			elif(extension == "ico"):
				self.set_header('Content-Type', 'image/ico')
				self.finish(open("../Interface"+fileToLoad, 'rb').read())
				return

			self.render("../Interface"+fileToLoad)

class QueryHandler(tornado.web.RequestHandler):
	def post(self):
		try:
			data = json.loads(self.request.body)
		except:
			self.write(json.dumps({"response":422, "message":"Query invalid!"}))
			return
		self.set_header('Content-Type', 'application/json')
		try:
		#Regulateur de lits
			if data["query"] == "RLglobalview":
				self.write(json.dumps(RL_GlobalView()))
			elif data["query"] == "RLunstablepatients":
				if "Service" in data:
					self.write(json.dumps(RL_UnstablePatients(data["Service"])))
				else:
					self.write(json.dumps(RL_UnstablePatients()))
			elif data["query"] == "RLtransferablepatients":
				self.write(json.dumps(RL_TransferablePatients()))
			elif data["query"] == "RLtransfintpatient":
				self.write(json.dumps(RL_TransfIntPatient()))
			elif data["query"] == "RLtransfextpatient":
				self.write(json.dumps(RL_TransfExtPatient()))
			elif data["query"] == "RLfreebeds":
				if "Service" in data:
					self.write(json.dumps(RL_FreeBeds("Service")))
				else:
					self.write(json.dumps(RL_FreeBeds()))
			elif data["query"] == "RLvectorsopen":
				self.write(json.dumps(RL_VectorsOpen()))
			elif data["query"] == "RLvectorsmodify":
				self.write(json.dumps(RL_VectorsModify(data["data"])))
		#Non réanimateur
			elif data["query"] == "MNfreebeds":
				if "Service" in data:
					self.write(json.dumps(MN_FreeBeds(data["Service"])))
				else:
					self.write(json.dumps(MN_FreeBeds()))
			elif data["query"] == "MNnewpatient":
				self.write(json.dumps(MN_NewPatient(data["data"])))
			elif data["query"] == "MNmodifypatientopen":
				self.write(json.dumps(MN_ModifyPatientOpen(data["Room"])))
			elif data["query"] == "MNmodifypatientsave":
				self.write(json.dumps(MN_ModifyPatientSave(data["data"])))
			elif data["query"] == "MNsearchpatient":
				self.write(json.dumps(MN_SearchPatient(data["Service"])))
		#Reanimateur
			elif data["query"] == "MRmainview":
				self.write(json.dumps(MR_MainView(data["Service"])))
			elif data["query"] == "MRunstableservice":
				self.write(json.dumps(MR_UnstableService(data["Service"])))
			elif data["query"] == "MRunstablepatient":
				self.write(json.dumps(MR_UnstablePatient(data["Room"])))
			elif data["query"] == "MRalltransfers":
				self.write(json.dumps(MR_AllTransfers(data["Service"])))
			elif data["query"] == "MRnewinttransferopen":
				self.write(json.dumps(MR_NewIntTransferOpen(data["Service"])))
			elif data["query"] == "MRnewinttransfersave":
				self.write(json.dumps(MR_NewIntTransferSave(data["data"])))
			elif data["query"] == "MRmodifytransfintopen":
				self.write(json.dumps(MR_ModifyTransfIntOpen(data["Room"])))
			elif data["query"] == "MRmodifytransfintsave":
				self.write(json.dumps(MR_ModifyTransfIntSave(data["data"])))
			elif data["query"] == "MRnewexttransferopen":
				self.write(json.dumps(MR_NewExtTransferOpen(data["Service"])))
			elif data["query"] == "MRnewexttransfersave":
				self.write(json.dumps(MR_NewExtTransferOpen(data["data"])))
			elif data["query"] == "MRmodifyexttransferopen":
				self.write(json.dumps(MR_NewExtTransferOpen(data["Room"])))
			elif data["query"] == "MRmodifyexttransfersave":
				self.write(json.dumps(MR_NewExtTransferSave(data["data"])))


			else:
				self.write(json.dumps({"response":404,"message":"Unknown Command"}))
		except:
			self.write(json.dumps({"response":500,"message":"Unknown Internal Error"}))


#
#       REGULATEUR DE LITS
#
def RL_GlobalView():
	result = {}
	r = SQLquery("""SELECT P.ConditionCode, COUNT(P.Room) 
					FROM PatForRea P 
					GROUP BY P.ConditionCode""")
	if "response" in r:
		return r
	result["UnstablePatients"] = [0,0,0]
	for i in r:
		result["UnstablePatients"][i["ConditionCode"]-1] = i["COUNT(P.Room)"]
	r = SQLquery("""SELECT COUNT(TI.Room), COUNT(TE.Room), SUM(S.EmptyBeds)
					FROM TransfInt TI, TransfExt TE, Services S""")
	if "response" in r:
		return r
	result["Transferable"] = [r[0]["COUNT(TI.Room)"], r[0]["COUNT(TE.Room)"]]
	result["FreeBeds"] = int(r[0]["SUM(S.EmptyBeds)"])
	result["response"] = 200
	return result

def RL_UnstablePatients(*argv):
	if len(argv) == 0:
		result =  GetAllUnstablePatients()
	else:
		result = GetUnstableService(argv[0])
	if "response" in result:
		return result
	result["response"] = 200
	return result

def RL_TransferablePatients(*argv):
	if len(argv) == 0:
		result = GetAllTransfers()
	else:
		result = GetServiceTransfer(argv[0])
	if "response" in result:
		return result
	result["response"] = 200
	return result

def RL_TransfIntPatient(Room):
	result = GetIntTransfer(Room)
	if "response" in result:
		return result
	result["response"]=200
	return result

def RL_TransfExtPatient(Room):
	result = GetExtTransfer(Room)
	if "response" in result:
		return result
	result["response"] = 200
	return result

def RL_FreeBeds(*argv):
	if len(argv) == 0:
		result = GetAllFreeBeds()
	else:
		result = GetServiceFreeBeds(argv[0])
	if "response" in result:
		return result
	result["response"] = 200
	return result

def RL_VectorsOpen():
	r = SQLquery("""SELECT *
					FROM Vectors V""")
	if "response" in r:
		return r
	result = {}
	for i in r:
		result[i["Name"]] = i["Amount"]
	result["response"] = 200
	return result

def RL_VectorsModify(data):
	if "Boats" not in data or "Cars" not in data or "Helicopters" not in data or "Planes" not in data or "TGV" not in data:
		return {"response":400, "message":"Incomplete data"}
	r = SQLquery(f"""UPDATE `Vectors` 
					SET `Amount` = {data["Boats"]} 
					WHERE `Vectors`.`Name` = 'Boats'""")
	if "response" in r:
		return r
	r = SQLquery(f"""UPDATE `Vectors` 
					SET `Amount` = {data["Cars"]} 
					WHERE `Vectors`.`Name` = 'Cars'""")
	if "response" in r:
		return r
	r = SQLquery(f"""UPDATE `Vectors` 
					SET `Amount` = {data["Helicopters"]} 
					WHERE `Vectors`.`Name` = 'Helicopters'""")
	if "response" in r:
		return r
	r = SQLquery(f"""UPDATE `Vectors` 
					SET `Amount` = {data["Planes"]}
					WHERE `Vectors`.`Name` = 'Planes'""")
	if "response" in r:
		return r
	r = SQLquery(f"""UPDATE `Vectors` 
					SET `Amount` = {data["TGV"]}
					WHERE `Vectors`.`Name` = 'TGV'""")
	if "response" in r:
		return r
	return {"response":200}



#
#       MEDECIN NON REANIMATEUR
#
def MN_FreeBeds(*argv):
	result = {}
	global db
	if len(argv) == 0:
		result = GetAllFreeBeds()
	else:
		result = GetServiceFreeBeds(argv[0])
	if "response" in result:
		return result
	result["response"] = 200
	return result

def MN_NewPatient(data):
	global db
	if "Room" not in data or "Service" not in data or "ConditionCode" not in data or "HasCovid" not in data or "O2" not in data or "SatO2" not in data or "Equipment" not in data:
		return {"response":400, "message":"Incomplete data"}
	r = SQLquery(f"""INSERT INTO `PatForRea` (`Room`, `Service`, `ConditionCode`, `HasCovid`, `O2`, `SatO2`) 
					VALUES ('{data["Room"]}', '{data["Service"]}', '{data["ConditionCode"]}', '{data["HasCovid"]}', '{data["O2"]}', '{data["SatO2"]}')""")
	if "response" in r:
		return r
	for i in data["Equipment"]:
		r = SQLquery(f"""INSERT INTO `EquipForRea` (`Patient`, `EquipmentCode`) 
						VALUES ('{data["Room"]}', '{i}')""")
		if "response" in r:
			return r
	return {"response": 200}

def MN_ModifyPatientOpen(Room):
	result = GetUnstablePatient(Room)
	result["response"] = 200
	return result

def MN_ModifyPatientSave(data):
	if "OldRoom" not in data:
		return {"response":400, "message":"Incomplete data"}
	r = SQLquery(f"""DELETE FROM EquipForRea WHERE Patient = '{data["OldRoom"]}'""")
	if "response" in r:
		return r
	if "NewRoom" not in data:
		r = SQLquery(f"""DELETE FROM `PatForRea` 
						WHERE `PatForRea`.`Room` = '{data["OldRoom"]}'""")
		if "response" in r:
			return r
	else:
		if "Service" not in data or "ConditionCode" not in data or "HasCovid" not in data or "O2" not in data or "SatO2" not in data:
			return {"response":400, "message":"Incomplete data"}
		r = SQLquery(f"""UPDATE `PatForRea` 
						SET `Room` = '{data["NewRoom"]}', `Service` = '{data["Service"]}', `ConditionCode` = '{data["ConditionCode"]}', `HasCovid` = '{data["HasCovid"]}', `O2` = '{data["O2"]}', `SatO2` = '{data["SatO2"]}' 
						WHERE `PatForRea`.`Room` = '{data["OldRoom"]}'""")
		if "response" in r:
			return r
		for item in data["Equipment"]:
			r = SQLquery(f"""INSERT INTO `EquipForRea` (`Patient`, `EquipmentCode`) 
							VALUES ('{data["NewRoom"]}', '{item}')""")
			if "response" in r:
				return r
	return {"response":200}

def MN_SearchPatient(Service):
	r = SQLquery(f"""SELECT P.Room, P.ConditionCode
					FROM PatForRea P
					WHERE P.Service = {Service}
					ORDER BY P.ConditionCode ASC""")
	if "response" in r:
		return r
	return {"response":200,"Patients":list(r)}



#
#       MEDECIN REANIMATEUR
#
def MR_MainView(Service):
	result = {}
	r = SQLquery(f"""SELECT S.Name, S.EmptyBeds
					FROM Services S
					WHERE S.UF = '{Service}'""")
	if "response" in r:
		return r
	result["Name"] = r[0]["Name"]
	result["FreeBeds"] = r[0]["EmptyBeds"]
	result["UnstablePatients"] = GetAllUnstablePatients()
	result["response"] = 200
	return result

def MR_UnstableService(Service):
	result = {"Patients":[]}
	r = SQLquery(f"""SELECT P.Room, P.ConditionCode
					FROM PatForRea P
					WHERE P.Service = {Service}
					ORDER BY P.ConditionCode ASC""")
	if "response" in r:
		return r
	for i in r:
		result["Patients"].append({"Room":i["Room"],"ConditionCode":i["ConditionCode"],"Equipment":[]})
	for i in range(len(result["Patients"])):
		r = SQLquery(f"""SELECT E.EquipmentCode
						FROM EquipForRea E
						WHERE E.Patient = '{result["Patients"][i]["Room"]}'""")
		if "response" in r:
			return r
		for j in r:
			result["Patients"][i]["Equipment"].append(j["EquipmentCode"])
	result["response"] = 200
	return result

def MR_UnstablePatient(Room):
	result = GetUnstablePatient(Room)
	result ["response"] = 200
	return result

def MR_AllTransfers(Service):
	result = GetServiceTransfer(Service)
	result["response"] = 200
	return result

def MR_NewIntTransferOpen(Service):
	result = {}
	r = SQLquery(f"""SELECT S.Name, S.BackRea
					FROM Services S
					WHERE S.UF = {Service}""")
	if "response" in r:
		return r
	result["Name"] = r[0]["Name"]
	result["Upgrade"] = r[0]["BackRea"]
	result["response"] = 200
	return result

def MR_NewIntTransferSave(data):
	if "Room" not in data or "Service" not in data:
		return {"response":400, "message":"Incomplete data"}
	r = SQLquery(f"""INSERT INTO `TransfInt` (`Room`, `Service`) 
					VALUES ('{data["Room"]}', {data["Service"]});""")
	if "response" in r:
		return r
	return {"response":200}

def MR_ModifyTransfIntOpen(Room):
	result = {}
	r = SQLquery(f"""SELECT S.Name, S.Backrea
					FROM Services S, TransfInt T
					WHERE T.Room = '{Room}' and S.UF = T.Service""")
	if "response" in r:
		return r
	result["Name"] = r[0]["Name"]
	result["Upgrade"] = r[0]["Backrea"]
	result["response"]=200
	return result

def MR_ModifyTransfIntSave(data):
	if "OldRoom" not in data:
		return {"response":400, "message":"Incomplete data"}
	if "NewRoom" not in data:
		r = SQLquery(f"""DELETE FROM `TransfInt` 
						WHERE `TransfInt`.`Room` = '{data["OldRoom"]}'""")
		if "response" in r:
			return r
	else:
		r = SQLquery(f"""UPDATE `TransfInt` 
						SET `Room` = '{data["NewRoom"]}'
						WHERE `TransfInt`.`Room` = '{data["OldRoom"]}'""")
		if "response" in r:
			return r
	return {"response":200}

def MR_NewExtTransferOpen(Service):
	result = {}
	r = SQLquery(f"""SELECT S.Name
					FROM Services S
					WHERE S.UF = {Service}""")
	if "response" in r:
		return r
	result["Name"] = r[0]["Name"]
	result["response"] = 200
	return result

def MR_NewExtTransferSave(data):
	if "Room" not in data or "Service" not in data or "Destination" not in data or "TravelMean" not in data:
		return {"response":400, "message":"Incomplete data"}
	r = SQLquery(f"""INSERT INTO `TransfExt` (`Room`, `Service`) 
					VALUES ('{data["Room"]}', {data["Service"]})""")
	if "response" in r:
		return r
	for i in data["Destination"]:
		r = SQLquery(f"""INSERT INTO `TransfExtTo` (`Room`, `TransfCode`) 
						VALUES ('{data["Room"]}', {i})""")
		if "response" in r:
			return r
	for i in data["TravelMean"]:
		r = SQLquery(f"""INSERT INTO `TransfExtBy` (`Room`, `TransfCode`) 
						VALUES ('{data["Room"]}', {i})""")
		if "response" in r:
			return r
	return {"response":200}

def MR_ModifyExtTransferOpen(Room):
	result = {}
	r = SQLquery(f"""SELECT S.Name
				FROM Services S, TransfExt T
				WHERE S.UF = T.Service AND T.Room = '{Room}'""")
	if "response" in r:
		return r
	result["Name"] = r[0]["Name"]
	r = SQLquery(f"""SELECT T.TransfCode
				FROM TransfExtTo T
				WHERE T.Room = '{Room}'""")
	if "response" in r:
		return r
	result["Destination"] = []
	for i in r:
		result["Destination"].append(i["TransfCode"])
	r = SQLquery(f"""SELECT T.TransfCode
				FROM TransfExtBy T
				WHERE T.Room = '{Room}'""")
	if "response" in r:
		return r
	result["TravelMean"] = []
	for i in r:
		result["TravelMean"].append(i["TransfCode"])
	result["response"] = 200
	return result

def MR_ModifyExtTransferSave(data):
	if "OldRoom" not in data:
		return {"response":400, "message":"Incomplete data"}
	r = SQLquery(f"""DELETE FROM `TransfExtBy` 
					WHERE `TransfExtBy`.`Room` = '{data["OldRoom"]}'""")
	if "response" in r:
		return r
	r = query(f"""DELETE FROM `TransfExtTo` 
					WHERE `TransfExtTo`.`Room` = '{data["OldRoom"]}'""")
	if "response" in r:
		return r
	if "NewRoom" not in data:
		r = SQLquery(f"""DELETE FROM `TransfExt` 
						WHERE `TransfExt`.`Room` = '{data["OldRoom"]}'""")
		if "response" in r:
			return r
	else:
		if "Destination" not in data or "TravelMean" not in data:
			return {"response":400, "message":"Incomplete data"}
		r = SQLquery(f"""UPDATE `TransfExt` 
						SET `Room` = '{data["NewRoom"]}'
						WHERE `TransfExt`.`Room` = '{data["OldRoom"]}'""")
		if "response" in r:
			return r
		for i in data["Destination"]:
			r = SQLquery(f"""INSERT INTO `TransfExtTo` (`Room`, `TransfCode`) 
						VALUES ('{data["NewRoom"]}', {i})""")
			if "response" in r:
				return r
		for i in data["TravelMean"]:
			r = SQLquery(f"""INSERT INTO `TransfExtBy` (`Room`, `TransfCode`) 
						VALUES ('{data["NewRoom"]}', {i})""")
			if "response" in r:
				return r
	return {"response":200} 












def SQLquery(query,kill=0):
	global db
	try:
		db.query(query)
		r = db.store_result()
		if r != None:
			r = r.fetch_row(how=1, maxrows=0)
			return r
		else:
			return {}
	except Exception as e:
		print(e)
		db = MySQLdb.connect(config.host, config.user, config.pswd, config.name, autocommit=True)
		return SQLquery(query,kill=1) if kill == 0 else {"response":500, "message":"SQL Error"}

def GetAllUnstablePatients():
	#get info
	r = SQLquery("""SELECT P.Service, P.ConditionCode, COUNT(P.Room) 
					FROM PatForRea P
					GROUP BY P.Service, P.ConditionCode""")
	if "response" in r:
		return r
	#create list
	LIST = []
	for service in r:
		flag = 0
		for index in range(len(LIST)):
			if LIST[index]["Service"] == service["Service"]:
				LIST[index]["Patients"][service["ConditionCode"]-1] = service["COUNT(P.Room)"]
				flag = 1
		if flag == 0:
			LIST.append({"Service":service["Service"], "Patients":[0,0,0]})
			LIST[len(LIST)-1]["Patients"][service["ConditionCode"]-1] = service["COUNT(P.Room)"]
	#sort list
	flag = 0
	while flag == 0:
		flag = 1
		for i in range(len(LIST)-1):
			if LIST[i]["Patients"][0] < LIST[i+1]["Patients"][0]:
				temp = LIST[i]
				LIST[i] = LIST[i+1]
				LIST[i+1] = temp
				flag = 0
			elif LIST[i]["Patients"][0] == LIST[i+1]["Patients"][0] and LIST[i]["Patients"][1] < LIST[i+1]["Patients"][1]:
				temp = LIST[i]
				LIST[i] = LIST[i+1]
				LIST[i+1] = temp
				flag = 0
			elif LIST[i]["Patients"][0] == LIST[i+1]["Patients"][0] and LIST[i]["Patients"][1] == LIST[i+1]["Patients"][1] and LIST[i]["Patients"][2] < LIST[i+1]["Patients"][2]:
				temp = LIST[i]
				LIST[i] = LIST[i+1]
				LIST[i+1] = temp
				flag = 0	
	#count all services
	result = {"GLOBAL":[0,0,0], "LIST":LIST}
	for service in result["LIST"]:
		for i in range(len(service["Patients"])):
			result["GLOBAL"][i] += service["Patients"][i]
	return result

def GetUnstableService(Service):
	r = SQLquery(f"""SELECT P.ConditionCode, COUNT(P.Room) 
					FROM PatForRea P
					WHERE P.Service = {Service}
					GROUP BY P.ConditionCode""")
	if "response" in r:
		return r
	result = {"Patient":[0,0,0]}
	for i in r:
		result["Patient"][i["ConditionCode"]-1] = i["COUNT(P.Room)"]
	return result

def GetUnstablePatient(Room):
	result = {}
	r = SQLquery(f"""SELECT * 
					FROM PatForRea P
					WHERE P.Room = '{Room}'""")
	if "response" in r:
		return r
	for key in r[0]:
		result[key] = r[0][key]
	r = SQLquery(f"""SELECT E.EquipmentCode 
					FROM EquipForRea E
					WHERE E.Patient = '{result["Room"]}'""")
	if "response" in r:
		return r
	result["Equipment"] = []
	for item in r:
		result["Equipment"].append(item["EquipmentCode"])
	return result

def GetAllTransfers():
	r = SQLquery("""SELECT COUNT(T.Room), T.Service, S.BackRea
					FROM TransfInt T, Services S
					WHERE T.Service = S.UF
					GROUP BY T.Service, S.BackRea""")
	if "response" in r:
		return r
	LIST = []
	for service in r:
		flag = 0
		for index in range(len(LIST)):
			if LIST[index]["Service"] == service["Service"]:
				LIST[index]["Upgrade"][(service["BackRea"]+1)%2] = service["COUNT(T.Room)"]
				flag = 1
		if flag == 0:
			LIST.append({"Service":service["Service"], "Upgrade":[0,0,0]})
			LIST[len(LIST)-1]["Upgrade"][(service["BackRea"]+1)%2] = service["COUNT(T.Room)"]
	r = SQLquery("""SELECT COUNT(T.Room), T.Service
					FROM TransfExt T
					GROUP BY T.Service""")
	if "response" in r:
		return r
	for service in r:
		flag = 0
		for index in range(len(LIST)):
			if LIST[index]["Service"] == service["Service"]:
				LIST[index]["Upgrade"][2] = service["COUNT(T.Room)"]
				flag = 1
		if flag == 0:
			LIST.append({"Service":service["Service"], "Upgrade":[0,0,service["COUNT(T.Room)"]]})
	flag = 0
	while flag == 0:
		flag = 1
		for i in range(len(LIST)-1):
			if LIST[i]["Upgrade"][0] < LIST[i+1]["Upgrade"][0]:
				temp = LIST[i]
				LIST[i] = LIST[i+1]
				LIST[i+1] = temp
				flag = 0
			elif LIST[i]["Upgrade"][0] == LIST[i+1]["Upgrade"][0] and LIST[i]["Upgrade"][1] < LIST[i+1]["Upgrade"][1]:
				temp = LIST[i]
				LIST[i] = LIST[i+1]
				LIST[i+1] = temp
				flag = 0
			elif LIST[i]["Upgrade"][0] == LIST[i+1]["Upgrade"][0] and LIST[i]["Upgrade"][1] == LIST[i+1]["Upgrade"][1] and LIST[i]["Upgrades"][2] < LIST[i+1]["Upgrade"][2]:
				temp = LIST[i]
				LIST[i] = LIST[i+1]
				LIST[i+1] = temp
				flag = 0
	result = {"GLOBAL":[0,0], "LIST": LIST}
	for service in LIST:
		result["GLOBAL"][0] += service["Upgrade"][0]
		result["GLOBAL"][0] += service["Upgrade"][1]
		result["GLOBAL"][1] += service["Upgrade"][2]
	return result

def GetServiceTransfer(Service):
	result = {"INTERNAL":[],"EXTERNAL":[]}
	r = SQLquery(f"""SELECT T.Room, S.BackRea
				FROM TransfInt T, Services S
				WHERE T.Service = {Service} AND S.UF = T.Service
				ORDER BY S.BackRea DESC""")
	if "response" in r:
		return r
	for i in r:
		result["INTERNAL"].append({"Room":i["Room"], "Upgrade":i["BackRea"]})
	r = SQLquery(f"""SELECT T.Room
					FROM TransfExt T
					WHERE T.Service = {Service}""")
	if "response" in r:
		return r
	for i in r:
		result["EXTERNAL"].append({"Room":i["Room"]})
	return result

def GetIntTransfer(Room):
	result = {}
	r = SQLquery(f"""SELECT S.Name, S.Backrea
					FROM Services S, TransfInt T
					WHERE T.Room = '{Room}' and S.UF = T.Service""")
	if "response" in r:
		return r
	result["Name"] = r[0]["Name"]
	result["Upgrade"] = r[0]["Backrea"]
	return result

def GetExtTransfer(Room):
	result = {}
	r = SQLquery(f"""SELECT S.Name
				FROM Services S, TransfExt T
				WHERE S.UF = T.Service AND T.Room = '{Room}'""")
	if "response" in r:
		return r
	result["Name"] = r[0]["Name"]
	r = SQLquery(f"""SELECT T.TransfCode
				FROM TransfExtTo T
				WHERE T.Room = '{Room}'""")
	if "response" in r:
		return r
	result["Destination"] = []
	for i in r:
		result["Destination"].append(i["TransfCode"])
	r = SQLquery(f"""SELECT T.TransfCode
				FROM TransfExtBy T
				WHERE T.Room = '{Room}'""")
	if "response" in r:
		return r
	result["TravelMean"] = []
	for i in r:
		result["TravelMean"].append(i["TransfCode"])
	return result

def GetAllFreeBeds():
	LIST = []
	r = SQLquery("""SELECT S.EmptyBeds, S.UF
					FROM Services S""")
	if "response" in r:
		return r
	for i in r:
		LIST.append({"Service":i["UF"],"FreeBeds":i["EmptyBeds"]})
	for service in range(len(LIST)):
		r = SQLquery(f"""SELECT S.Phone, S.Name
						FROM Services S
						WHERE S.UF = {LIST[service]["Service"]}""")
		if "response" in r:
			return r
		LIST[service]["Phone"] = r[0]["Phone"]
		LIST[service]["Name"] = r[0]["Name"]
		r = SQLquery(f"""SELECT E.EquipmentCode
						FROM EquipFromRea E
						WHERE E.Service = {LIST[service]["Service"]}""")
		if "response" in r:
			return r
		LIST[service]["Equipment"] = []
		for i in r:
			LIST[service]["Equipment"].append(i["EquipmentCode"])
	flag = 0
	while flag == 0:
		flag = 1
		for i in range(len(LIST)-1):
			if LIST[i]["FreeBeds"] < LIST[i+1]["FreeBeds"]:
				temp = LIST[i]
				LIST[i] = LIST[i+1]
				LIST[i+1] = temp
				flag = 0
	result = {"GLOBAL":0, "LIST":LIST}
	for service in LIST:
		result["GLOBAL"] += service["FreeBeds"]
	return result

def GetServiceFreeBeds(Service):
	result = {}
	r = SQLquery(f"""SELECT S.EmptyBeds
					FROM Services S
					WHERE S.UF = {Service}""")
	if "response" in r:
		return r
	result["FreeBeds"] = r[0]["EmptyBeds"]
	r = SQLquery(f"""SELECT S.Phone, S.Name
					FROM Services S
					WHERE S.UF = {Service}""")
	if "response" in r:
		return r
	result["Phone"] = r[0]["Phone"]
	result["Name"] = r[0]["Name"]
	r = SQLquery(f"""SELECT E.EquipmentCode
					FROM EquipFromRea E
					WHERE E.Service = {Service}""")
	if "response" in r:
		return r
	result["Equipment"] = []
	for i in r:
		result["Equipment"].append(i["EquipmentCode"])
	return result






#interne upgrade - interne downgrade - externe



def make_app():
	return tornado.web.Application([
		(r"/query", QueryHandler),
		(r"/.*", MainPage)
	])

if __name__ == "__main__":    
	http = tornado.httpserver.HTTPServer(make_app(), ssl_options={
		"certfile": "/home/lauzhackTeam/certs/live/lauzhack.sysmic.ch/fullchain.pem",
		"keyfile": "/home/lauzhackTeam/certs/live/lauzhack.sysmic.ch/privkey.pem",
	})
	http.listen(8080)
	tornado.autoreload.start()
	for dir, _, files in os.walk("../Interface"):
		for file in files:
			if(not file.startswith(".")):
				tornado.autoreload.watch(dir + '/' + file)

	tornado.ioloop.IOLoop.current().start()
