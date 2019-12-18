const https = require("https");
const aws = require("aws-sdk");
const azureADDomain = process.env["AzureADDomain"];
const dynamicsHostDomain = process.env["DynamicsHostDomain"];
const dynamicsClientId = process.env["DynamicsClientId"];
const dynamicsClientSecret = process.env["DynamicsClientSecret"];
const authHost = "login.windows.net";
const grantType = "client_credentials";
const azureADAuthPath = "/" + azureADDomain + "/oauth2/token";
const dynamicsResourceUrl = "https://" + dynamicsHostDomain;

exports.handler = (event, context, callback) => {
  console.log(
    "Starting auth request against token endpoint at: " +
      azureADAuthPath +
      " for Dynamics 365 instance: " +
      dynamicsResourceUrl +
      " using Azure Client Id: " +
      dynamicsClientId
  );

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
        const parsedAuthResponse = JSON.parse(authResponse);
        const accessToken = parsedAuthResponse.access_token;
        const accessTokenExpiresIn = parsedAuthResponse.expires_in;
        const accessTokenExpiresAt = parsedAuthResponse.expires_on;
        var accessTokenExpiryDate = new Date(0);
        accessTokenExpiryDate.setUTCSeconds(accessTokenExpiresAt);
        console.log(
          "Got new token that will expire in " +
            Math.round(accessTokenExpiresIn / 60) +
            " minutes at " +
            accessTokenExpiryDate
        );
        const result = {
          accessToken: accessToken,
          expiryDate: accessTokenExpiryDate
        };
        callback(null, result);
      } else {
        var badResponseCodeMsg =
          "Could not get access token for Dynamics 365 Web API. Response code " +
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

        var ses = new aws.SES();
        var params = {
          Destination: {
            ToAddresses: ["${NotificationEmailAddress}"]
          },
          Message: {
            Body: {
              Html: {
                Charset: "UTF-8",
                Data:
                  "<b>Amazon Connect Microsoft Dynamics 365 Integration failed to authenticate</b><br/>Lambda function failed to get an access token. Please check the error below<br/>" +
                  badResponseCodeMsg
              }
            },
            Subject: {
              Charset: "UTF-8",
              Data:
                "Amazon Connect Microsoft Dynamics 365 Integration failed to authenticate"
            }
          },
          Source: "${NotificationEmailAddress}"
        };
        ses.sendEmail(params, function(err, data) {
          if (err) console.error("Failed to send notification email", err);
        });

        callback(badResponseCodeMsg);
      }
    });
  });

  authRequestClient.on("error", function(e) {
    console.error("Auth request failed with error", e);
    callback("Auth request failed with error: " + e);
  });

  authRequestClient.write(authRequestBody);
  authRequestClient.end();
};
