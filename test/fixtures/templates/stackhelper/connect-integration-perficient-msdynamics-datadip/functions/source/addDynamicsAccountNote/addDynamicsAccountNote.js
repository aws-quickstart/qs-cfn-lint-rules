const https = require("https");
var aws = require("aws-sdk");
const dynamicsHostDomain = process.env["DynamicsHostDomain"];
const getDynamicsTokenLambdaName = process.env["GetDynamicsTokenLambdaName"];
const awsRegionForDynamicsTokenLambda = process.env["AWSRegion"];
var accessToken = "";

exports.handler = (event, context, callback) => {
  const invokedByCloudWatchEvent =
    event.Name == "CloudWatchEvent" && event.Type == "KeepWarm";

  if (accessToken == "" || invokedByCloudWatchEvent) {
    getAccessTokenAndThenAddNote(
      event.Details,
      callback,
      !invokedByCloudWatchEvent
    );
  } else {
    addNote(event.Details, callback);
  }
};

function getAccessTokenAndThenAddNote(contactDetails, callback, addRealNote) {
  var lambda = new aws.Lambda({
    region: awsRegionForDynamicsTokenLambda
  });
  lambda.invoke(
    {
      FunctionName: getDynamicsTokenLambdaName,
      Payload: ""
    },
    function(error, data) {
      if (error) {
        callback("Failed to invoke Lambda to get new access token: " + error);
      }
      if (data) {
        var payloadObject = JSON.parse(data.Payload);
        console.log("Got Dynamics API access token");
        accessToken = payloadObject.accessToken;
        if (addRealNote) {
          addNote(contactDetails, callback);
        } else {
          https.get(
            "https://" +
              dynamicsHostDomain +
              "/api/data/v8.2/accounts?%24select=name&%24top=1",
            response => {}
          );
          callback(null, "OK");
        }
      }
    }
  );
}

function addNote(contactDetails, callback) {
  var accountId = contactDetails.ContactData.Attributes.DynamicsAccountId;
  var callerPhoneNumber = contactDetails.ContactData.CustomerEndpoint.Address;
  callerPhoneNumber = callerPhoneNumber.replace(/^\+[0-9]/, ""); //strip +1
  var queueName = "Not set";
  if (contactDetails.ContactData.Queue) {
    queueName = contactDetails.ContactData.Queue.Name;
  }
  var connectPhoneNumber = "Unknown";
  if (contactDetails.ContactData.SystemEndpoint) {
    connectPhoneNumber = contactDetails.ContactData.SystemEndpoint.Address;
    connectPhoneNumber = connectPhoneNumber.replace(/^\+[0-9]/, ""); //strip +1
  }

  console.log(
    "Adding Note for Connect call from " +
      callerPhoneNumber +
      " to Account " +
      accountId
  );

  const subject = "Amazon Connect call received from " + callerPhoneNumber;
  var notetext = "Caller dialed " + connectPhoneNumber + " \n";
  if (queueName != "Not set") {
    notetext += "Caller was placed into " + queueName + " queue";
  }

  var note = {
    subject: subject,
    notetext: notetext
  };
  note["objectid_account@odata.bind"] = "accounts(" + accountId + ")";
  var noteRequestBody = JSON.stringify(note);

  var callRequestHeaders = {
    Authorization: "Bearer " + accessToken,
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": noteRequestBody.length,
    "OData-MaxVersion": "4.0",
    "OData-Version": "4.0",
    Accept: "application/json"
  };

  var options = {
    host: dynamicsHostDomain,
    path: "/api/data/v8.2/annotations",
    method: "POST",
    headers: callRequestHeaders
  };

  var noteRequestClient = https.request(options, function(response) {
    var insertPhoneCallResponse = "";

    response.on("data", function(dataChunk) {
      insertPhoneCallResponse += dataChunk;
    });

    response.on("end", function() {
      if (response.statusCode == 204) {
        callback(null, { success: true });
      } else {
        var badResponseCodeMsg =
          "Could not add Note to account. Response code " +
          response.statusCode +
          ", message: " +
          response.statusMessage;
        console.error(badResponseCodeMsg);
        callback(badResponseCodeMsg);
      }
    });
  });

  noteRequestClient.on("error", function(e) {
    console.error("Add Note request failed with error", e);
    callback("Add Note request failed with error: " + e);
  });

  noteRequestClient.write(noteRequestBody);
  noteRequestClient.end();
}
