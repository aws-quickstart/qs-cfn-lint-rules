package templates

//go:generate go run -tags=dev generate.go

import (
	"github.com/cf-platform-eng/aws-pcf-quickstart/config"
	"github.com/starkandwayne/om-tiler/pattern"
)

func GetPattern(cfg *config.Config, varsStore string, expectAllKeys bool) (pattern.Pattern, error) {
	var opsFiles []string
	if cfg.PcfDeploymentSize == "Starter" {
		opsFiles = append(opsFiles, "options/starter.yml")
	}
	if cfg.PcfDeploymentSize == "Multi-AZ" {
		opsFiles = append(opsFiles, "options/full.yml")
	}
	return pattern.NewPattern(pattern.Template{
		Store:    Templates,
		Manifest: "deployment.yml",
		OpsFiles: opsFiles,
		Vars:     cfg.Raw,
	}, varsStore, expectAllKeys)
}
