const https = require("https");
const aws = require("aws-sdk");
const cfnResponse = require("cfn-response");
var accessToken = "invalidToken";

exports.handler = (event, context, callback) => {
  if (event["RequestType"] == "Create") {
    checkDynamicsWebApiUrl(event, context, callback);
  } else {
    console.log("Skipping function test for update or removal of Quick Start");
    cfnResponse.send(event, context, cfnResponse.SUCCESS);
  }
};

function checkDynamicsWebApiUrl(event, context, callback) {
  console.log(
    "Validating that we have the correct URL to the Dynamics 365 Web API based on the Quick Start template parameters"
  );

  var dynamicsHostDomain = event["ResourceProperties"]["DynamicsHostDomain"];
  console.log(
    "Template parameter for Dynamics 365 Domain: " + dynamicsHostDomain
  );

  var dynamicsWebApiBasePath = "/api/data/v8.2";

  var dynamicsRequestHeaders = {
    Authorization: "Bearer " + accessToken,
    Accept: "application/json"
  };

  var requestParams = {
    host: dynamicsHostDomain,
    path: dynamicsWebApiBasePath,
    method: "GET",
    headers: dynamicsRequestHeaders
  };

  https
    .get(requestParams, response => {
      var lookupResponseBody = "";

      response.on("data", dataChunk => {
        lookupResponseBody += dataChunk;
      });

      response.on("end", function() {
        if (response.statusCode == 401) {
          console.log(
            "Got 401 Unauthorized response as we expect with an invalid token"
          );
          console.log(
            "Checking WWW-Authenticate header for the requested resource to validate we are hitting the Dynamics 365 Web API"
          );
          var wwwAuthenticateHeader = response.headers["www-authenticate"];
          var headerContainsDynamicsDomain =
            wwwAuthenticateHeader &&
            wwwAuthenticateHeader.indexOf(dynamicsHostDomain) > 1;
          if (headerContainsDynamicsDomain) {
            console.log(
              "Success! WWW-Authenticate header contains Dynamics 365 Domain"
            );
            cfnResponse.send(event, context, cfnResponse.SUCCESS);
          } else {
            var failMsg =
              "Please check the Dynamics 365 Domain parameter to ensure it corresponds to your Dynamics 365 instance. WWW-Authenticate header did not contain Dynamics 365 Domain: " +
              wwwAuthenticateHeader;
            console.error(failMsg);
            cfnResponse.send(event, context, cfnResponse.FAILED, {
              error: failMsg
            });
          }
        } else {
          var failMsg =
            "Please check the Dynamics 365 Domain parameter to ensure it corresponds to your Dynamics 365 instance. Got non-401 response: " +
            response.statusCode +
            " " +
            response.statusMessage;
          console.error(failMsg);
          cfnResponse.send(event, context, cfnResponse.FAILED, {
            error: failMsg
          });
        }
      });
    })
    .on("error", e => {
      var failMsg =
        "Please check the Dynamics 365 Domain parameter to ensure it corresponds to your Dynamics 365 instance. Error occurred: " +
        e;
      console.error(failMsg);
      cfnResponse.send(event, context, cfnResponse.FAILED, {
        error: failMsg
      });
    });
}
