(input | split(":")) as $vals|
{
  "Filename":$vals[0],
  "linenumber":$vals[1],
  "Level":"Error",
  "Location":{
    "Start":{
      "LineNumber":$vals[1]|tonumber,
      "ColumnNumber":0
    },
    "End":{
      "LineNumber":$vals[1]|tonumber,
      "ColumnNumber":0}
    },
    "Message":"[git-secrets] Disallowed pattern found",
    "Rule":{
      "Id":"GitSecrets",
      "Description":"Validate data against git-secrets",
      "Source":"https://github.com/aws-quickstart/qs-cfn-lint-rules"
    }
}
