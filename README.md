# AWS Quick Start cfn-lint rules

This repo provides CloudFormation linting rules specific to [AWS Quick Start](https://aws.amazon.com/quickstart/)
guidelines, for more information see the [Contributors Guide](https://aws-quickstart.github.io).

## Installation and Usage

```bash
cd ~/
git clone https://github.com/aws-quickstart/qs-cfn-lint-rules.git
cd qs-cfn-lint-rules
pip install -e .
```

To add the rules when running on the command line use the `-a` flag to add the additional rules:

```bash
cfn-lint my-cfn-template.yaml -a ~/qs-cfn-lint-rules/qs_cfn_lint_rules/
```

To use in your IDE install the relevant
[cfn-lint plugin](https://github.com/aws-cloudformation/cfn-python-lint#editor-plugins) and add the rules to your
cfn-lint config file (`~/.cfnlintrc`) as follows:

```yaml
append_rules:
- ~/qs-cfn-lint-rules/qs_cfn_lint_rules/
```

## Vim Specfic Instructions (using vundle and syntastic)

![image](https://user-images.githubusercontent.com/5912128/55508631-22366880-560f-11e9-867f-baa516712f63.png)

### Install the plugins

**Add to `syntastic` and `vim-cfn` your `~/.vimrc`:**

__Add to vundle plugin section:__

```vim
"---------------------------=== CloudFormation  ===------------------------------
Plugin 'scrooloose/syntastic'        " Syntax checking plugin for Vim
Plugin 'speshak/vim-cfn'             "CloudFormation syntax checking/highlighting
```

#### Install plugins

```bash
vim +PluginInstall +qall
```

### Set statusline and triggers

**Append to the bottom of your `~/.vimrc`**

```vim
"cfn-lint
set statusline+=%#warningmsg#
set statusline+=%{SyntasticStatuslineFlag()}
set statusline+=%*

let g:syntastic_always_populate_loc_list = 1
let g:syntastic_auto_loc_list = 1
let g:syntastic_check_on_open = 1
let g:syntastic_check_on_wq = 0
let g:syntastic_cloudformation_checkers = ['cfn_lint']
```

### Set FileTypes for vim-cfn

**Add to `~/.vim/bundle/vim-cfn/ftdetect/cloudformation.vim`**

```vim
autocmd BufNewFile,BufRead *.template setfiletype yaml.cloudformation
autocmd BufNewFile,BufRead *.template.yaml setfiletype yaml.cloudformation
```

### Update syntastic plugin

Add the following to ~/.vim/after/plugin/syntastic.vim:

```vim
let g:syntastic_cloudformation_checkers = ['cfn_lint']
```

## Troubleshooting

### Custom dictionary

If you receive spelling error warnings [9006] for words that are spelled correctly, such as the example below, AWS service names, or words that should be excluded from all future linting, please add these words to `./qs_cfn_lint_rules/data/custom_dict.txt`.

```text
line 93 [9006] Parameter QSS3BucketName contains spelling error(s):
{'customizing'}
```

For spelling exclusions for a specific CloudFormation template, such as partner brand names, please add these words to a `LintSpellExclude` list to the `Metadata` section.

```yaml
Metadata:
  LintSpellExclude:
    - PartnerName
```

### Sentence case

If you receive sentence case warnings [9006] for words that should be capitalized, such as partner product names, please add a `SentenceCaseExclude` list to the `Metadata` section.

```yaml
Metadata:
  SentenceCaseExclude:
    - Pro
```
