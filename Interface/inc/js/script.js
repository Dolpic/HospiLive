
function sendRequest(jsonObject, callback){
    var url   = "https://lauzhack.sysmic.ch:8080/query";
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200)
            callback(xhttp.responseText)
    };
    xhttp.open("POST", url);
    xhttp.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.send(JSON.stringify(jsonObject));
}

function $_GET(param) {
  str = window.location.href
  if(str.split('?')[1] == undefined)
    return undefined
  args_str = str.split('?')[1]
  args = args_str.split('&')
  var collect_args = new Map()
  args.forEach(function(current){
    arg =current.split('=')
    collect_args.set(arg[0], arg[1])
  });
  if (param == undefined){
    return collect_args;
  } else {
    return collect_args.get(param)
  }
}
//-------------------------------------BEDS REGULATORS-------------------------------------------------
//----------PAGE 1----------

function RLglobalview(){
    var jsonObject = {"query" : "RLglobalview"}
    sendRequest(jsonObject, function(result){
      console.log("Bed regulators first page data retrieved : ")
      console.log(JSON.parse(result))
      var parsed = JSON.parse(result)
      RegulateurDeLitMainPage(parsed.UnstablePatients, parsed.Transferable, parsed.FreeBeds)
    })
}

//----------TRANSFERABLES----------

function RLtransferablepatients(){
    var jsonObject = {"query" : "RLtransferablepatients"}
    sendRequest(jsonObject, function(result){
      console.log("Information about transferables : ")
      console.log(JSON.parse(result))
    })
}

//----------AVAILABLE BEDS----------

function RLfreebeds(callback){
    var jsonObject = {"query" : "RLfreebeds"}
    sendRequest(jsonObject, function(result){
      callback(JSON.parse(result))
    })
}

//----------UNSTABLE PATIENTS----------

function RLunstablepatients(service){
    var jsonObject;
    if (service == undefined){
      jsonObject = {"query" : "RLunstablepatients"}
      sendRequest(jsonObject, function(result){
        parsed = JSON.parse(result)
        PatientsInstables(parsed)
      })
    }
    else {
      jsonObject = {"query" : "RLunstablepatients", "Service" : service}
      sendRequest(jsonObject, function(result){
        parsed = JSON.parse(result)
        PatientsInstablesDetails(parsed ,service)
      })
    }
}

function RLgetVectors(callback){
  jsonObject = {"query" : "RLvectorsopen"}
  sendRequest(jsonObject, function(result){
    callback(JSON.parse(result))
  })
}

//-------------------------------------NON REANIMATORS-------------------------------------------------
function MNfreebeds(service){
    var jsonObject;
    if (service == undefined){
      jsonObject = {"query" : "MNfreebeds"}
      sendRequest(jsonObject, function(result){
        parsed = JSON.parse(result)
        FreedBedsNonReaminators(parsed.LIST)
      })
    }
    else {
      jsonObject = {"query" : "MNfreebeds", "Service" : service}
      sendRequest(jsonObject, function(result){
        FreeBedsCount(JSON.parse(result))
      })
    }
}

function MNsearchpatient(service){
    var jsonObject = {"query" : "MNsearchpatient", "Service" : service}
    sendRequest(jsonObject, function(result){
      addResultsPatientsRepertories(JSON.parse(result));
    })
}

function MNmodifypatientopen(roomNumber, callback){
  var jsonObject = {"query" : "MNmodifypatientopen", "Room" : roomNumber}
  sendRequest(jsonObject, function(result){
    callback(JSON.parse(result))
  })
}

function MNmodifypatientsave(data){
  var jsonObject = {"query" : "MNmodifypatientopen", "data" : data}
    sendRequest(jsonObject, function(result){
  })
}

function MNmodifypatientnew(data){
  var jsonObject = {"query" : "MNnewpatient", "data" : data}
    sendRequest(jsonObject, function(result){
  })
}

//-------------------------------------REANIMATORS-------------------------------------------------
//----------PAGE 1----------

function getEssentialInfos(service, callback){
    var jsonObject = {"query" : "MRmainview", "Service" : service}
    sendRequest(jsonObject, function(result){
      callback(JSON.parse(result))
    })
}

//-----------ADD PATIENT----------

function addPatient(patientID, chamber,hasCovid,conditionCode,needsDescription){
    var jsonObject = {"query": "addPatient", "PatientID":patientID,"chamber":chamber,"hasCovid":hasCovid,"conditionCode":conditionCode,"needsDescription":needsDescription}
    sendRequest(jsonObject, function(result){
        console.log("New Patient added with following data : ")
        console.log(JSON.parse(result))
    })
}

//----------MODIFY PATIENT----------

function modifyPatient(patientID, chamber,hasCovid,conditionCode,needsDescription){
    var jsonObject = {"query": "addPatient", "PatientID":patientID,"chamber":chamber,"hasCovid":hasCovid,"conditionCode":conditionCode,"needsDescription":needsDescription}
    sendRequest(jsonObject, function(result){
        console.log("Modify patient with following : ")
        console.log(JSON.parse(result))
    })
}
