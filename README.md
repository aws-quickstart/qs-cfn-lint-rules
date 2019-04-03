# AWS Quick Start cfn-lint rules

This repo provides CloudFormation linting rules specific to [AWS Quick Start](https://aws.amazon.com/quickstart/) 
guidelines, for more information see the [Contributors Guide](https://aws-quickstart.github.io).

## Installation and Usage

```bash
cd ~/
git clone https://github.com/aws-quickstart/qs-cfn-lint-rules.git
pip install -e .
```

To add the rules when running on the command line use the `-a` flag to add the additional rules:

```bash
cfn-lint my-cfn-template.yaml -a ~/qs-cfn-lint-rules/qs-cfn-lint-rules/
```

To use in your IDE install the relevant 
[cfn-lint plugin](https://github.com/aws-cloudformation/cfn-python-lint#editor-plugins) and add the rules to your 
cfn-lint config file (`~/.cfnlintrc`) as follows:

```yaml
append_rules:
- ~/qs-cfn-lint-rules/qs-cfn-lint-rules/
```

## Vim Specfic Instructions (using vundle and syntastic)
![image](https://user-images.githubusercontent.com/5912128/55508631-22366880-560f-11e9-867f-baa516712f63.png)
### Install the plugins:
**Add to `syntastic` and `vim-cfn` your `~/.vimrc`:**

__Add to vundle plugin section:__

```
"---------------------------=== Cloudfromation  ===------------------------------
Plugin 'scrooloose/syntastic'        " Syntax checking plugin for Vim
Plugin 'speshak/vim-cfn'             "CloudFormation syntax checking/highlighting
```

**Install plugins**

`vim +PluginInstall +qall`

### Set statusline and triggers:

**Append to the bottom of your `~/.vimrc`:**
```
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

### Set FileTypes for vim-cfn:

**Add to  `~/.vim/bundle/vim-cfn/ftdetect/cloudformation.vim`**
``` 
autocmd BufNewFile,BufRead *.template setfiletype yaml.cloudformation
autocmd BufNewFile,BufRead *.template.yaml setfiletype yaml.cloudformation
```
### Update syntastic pluging
Add the following to ~/.vim/after/plugin/syntastic.vim:

`let g:syntastic_cloudformation_checkers = ['cfn_lint']`
