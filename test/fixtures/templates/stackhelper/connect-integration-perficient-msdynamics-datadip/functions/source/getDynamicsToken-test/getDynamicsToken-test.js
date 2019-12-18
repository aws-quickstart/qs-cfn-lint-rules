const https = require("https");
const cfnResponse = require("cfn-response");
const authHost = "login.windows.net";
const grantType = "client_credentials";

exports.handler = (event, context, callback) => {
  if (event["RequestType"] == "Create") {
    checkIfCanGetAccessToken(event, context, callback);
  } else {
    console.log("Skipping function test for update or removal of Quick Start");
    cfnResponse.send(event, context, cfnResponse.SUCCESS);
  }
};

function checkIfCanGetAccessToken(event, context, callback) {
  console.log(
    "Validating that we can get an access token from Azure AD for Dynamics 365 based on the Quick Start template parameters"
  );
  const azureADDomain = event["ResourceProperties"]["AzureADDomain"];
  console.log("Template parameter for Azure AD Domain: " + azureADDomain);
  const dynamicsHostDomain = event["ResourceProperties"]["DynamicsHostDomain"];
  console.log(
    "Template parameter for Dynamics 365 Domain: " + dynamicsHostDomain
  );
  const dynamicsClientId = event["ResourceProperties"]["DynamicsClientId"];
  console.log("Template parameter for Dynamics Client Id: " + dynamicsClientId);
  const dynamicsClientSecret =
    event["ResourceProperties"]["DynamicsClientSecret"];
  console.log(
    "Not showing template parameter value for Dynamics Client Secret because it's a secret"
  );
  const azureADAuthPath = "/" + azureADDomain + "/oauth2/token";
  const dynamicsResourceUrl = "https://" + dynamicsHostDomain;

  var authRequestBody = "";
  authRequestBody += "grant_type=" + encodeURIComponent(grantType);
  authRequestBody += "&resource=" + encodeURIComponent(dynamicsResourceUrl);
  authRequestBody += "&client_id=" + encodeURIComponent(dynamicsClientId);
  authRequestBody +=
    "&client_secret=" + encodeURIComponent(dynamicsClientSecret);

  const authRequestHeaders = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Content-Length": Buffer.byteLength(authRequestBody)
  };

  const options = {
    host: authHost,
    path: azureADAuthPath,
    method: "POST",
    headers: authRequestHeaders
  };

  var authRequestClient = https.request(options, function(response) {
    var authResponse = "";
    response.setEncoding("utf8");

    response.on("data", function(dataChunk) {
      authResponse += dataChunk;
    });

    response.on("end", function() {
      if (response.statusCode == 200) {
        console.log("Success! Got Dynamics 365 access token!");
        cfnResponse.send(event, context, cfnResponse.SUCCESS);
      } else {
        var failMsg =
          "Dynamics 365 access token request failed. Please validate the Azure AD Domain, Dynamics Host Domain, Dynamics Client Id and Dynamics Secret Id parameters. Response code was " +
          response.statusCode +
          ". ";
        console.error(failMsg);
        cfnResponse.send(event, context, cfnResponse.FAILED, {
          error: failMsg
        });
      }
    });
  });

  authRequestClient.on("error", function(e) {
    var failMsg =
        "Dynamics 365 access token request failed. Please validate the Azure AD Domain, Dynamics Host Domain, Dynamics Client Id and Dynamics Secret Id parameters. ",
      e;
    console.error(failMsg);
    cfnResponse.send(event, context, cfnResponse.FAILED, {
      error: failMsg
    });
  });

  authRequestClient.write(authRequestBody);
  authRequestClient.end();
}
