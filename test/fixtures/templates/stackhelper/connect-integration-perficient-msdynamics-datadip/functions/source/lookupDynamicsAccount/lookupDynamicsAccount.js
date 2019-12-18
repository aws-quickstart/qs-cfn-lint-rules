const https = require("https");
var aws = require("aws-sdk");
const dynamicsHostDomain = process.env["DynamicsHostDomain"];
const getDynamicsTokenLambdaName = process.env["GetDynamicsTokenLambdaName"];
const awsRegionForDynamicsTokenLambda = process.env["AWSRegion"];
var accessToken = "";

exports.handler = (event, context, callback) => {
  const invokedByCloudWatchEvent =
    event.Name == "CloudWatchEvent" && event.Type == "KeepWarm";
  if (invokedByCloudWatchEvent) {
    console.log(
      "Invoked by Cloud Watch Event. Will get token and do dummy lookup query to keep Lambda warm"
    );
  }

  if (accessToken == "" || invokedByCloudWatchEvent) {
    getAccessTokenAndThenLookupAccountByPhone("+15551234567", callback);
  } else {
    lookupAccountByPhone(
      event.Details.ContactData.CustomerEndpoint.Address,
      callback
    );
  }
};

function getAccessTokenAndThenLookupAccountByPhone(
  callerPhoneNumber,
  callback
) {
  console.log("Requesting Dynamics API access token");
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
        console.error("Failed to invoke Lambda to get new access token", error);
        callback("Failed to invoke Lambda to get new access token: " + error);
      }
      if (data) {
        var payloadObject = JSON.parse(data.Payload);
        console.log("Got Dynamics API access token");
        accessToken = payloadObject.accessToken;
        lookupAccountByPhone(callerPhoneNumber, callback);
      }
    }
  );
}

function lookupAccountByPhone(callerPhoneNumber, callback) {
  callerPhoneNumber = callerPhoneNumber.replace(/^\+[0-9]/, ""); //strip +1
  console.log(
    "Starting Dynamics account lookup for number " +
      callerPhoneNumber +
      " from Dynamics instance at " +
      dynamicsHostDomain
  );

  var dynamicsLookupQuery =
    "/api/data/v8.2/accounts?$select=name&$top=1&$filter=startswith(telephone1,%27" +
    callerPhoneNumber +
    "%27)";

  var dynamicsLookupRequestHeaders = {
    Authorization: "Bearer " + accessToken,
    Accept: "application/json"
  };

  var lookupRequestParams = {
    host: dynamicsHostDomain,
    path: dynamicsLookupQuery,
    method: "GET",
    headers: dynamicsLookupRequestHeaders
  };

  https
    .get(lookupRequestParams, response => {
      var lookupResponseBody = "";

      response.on("data", dataChunk => {
        lookupResponseBody += dataChunk;
      });

      response.on("end", function() {
        if (response.statusCode == 200) {
          const parsedLookupResponseEnvelope = JSON.parse(lookupResponseBody);
          if (parsedLookupResponseEnvelope.value.length == 0) {
            console.log(
              "Account look up for " + callerPhoneNumber + " found no results"
            );
            const result = {
              accountId: "NotFound",
              accountName: "NotFound",
              accountPhoneNumber: callerPhoneNumber
            };
            callback(null, result);
          } else {
            console.log("Found Dynamics account for " + callerPhoneNumber);
            const firstAccountFound = parsedLookupResponseEnvelope.value[0];
            const result = {
              accountId: firstAccountFound.accountid,
              accountName: firstAccountFound.name,
              accountPhoneNumber: callerPhoneNumber
            };
            callback(null, result);
          }
        } else {
          var badResponseCodeMsg =
            "Could not find account. Response code " +
            response.statusCode +
            ", message: " +
            response.statusMessage;
          if (response.statusCode == 401 || response.statusCode == 403) {
            badResponseCodeMsg =
              "Dynamics returned response " +
              response.statusCode +
              ", please ensure you have provisioned the security profile for the user in accordance with the user guide. " +
              response.statusMessage;
          }
          console.error(badResponseCodeMsg);
          callback(badResponseCodeMsg);
        }
      });
    })
    .on("error", e => {
      console.error("Account lookup request failed with error: ", e);
      callback("Account lookup failed with error: " + e);
    });
}
