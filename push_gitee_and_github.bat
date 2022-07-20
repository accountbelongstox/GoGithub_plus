git add .
git branch -M "master"
git commit -m "new amend"
set git_name = gitee
set git_url = git@gitee.com:accountbelongstox/GoGitHub_plus.git
git remote add %git_name% %git_url%
git push -u %git_name% master --force
set git_name = github
set git_url = git@github.com:accountbelongstox/GoGithub_plus.git
git remote add %git_name% %git_url%
git branch -M "main"
git commit -m "new amend"
git push -u %git_name% main --force
cmd