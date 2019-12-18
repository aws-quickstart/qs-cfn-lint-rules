// +build ignore

package main

import (
	"log"

	"github.com/cf-platform-eng/aws-pcf-quickstart/templates"

	"github.com/shurcooL/vfsgen"
)

func main() {
	err := vfsgen.Generate(templates.Templates, vfsgen.Options{
		PackageName:  "templates",
		BuildTags:    "!dev",
		VariableName: "Templates",
	})
	if err != nil {
		log.Fatalln(err)
	}
}
