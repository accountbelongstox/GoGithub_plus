rem git remote add gitee git@gitee.com:accountbelongstox/GoGitHub_plus.git
git branch -M "master"
git add .
git commit -m "new amend"
ssh -T git@gitee.com
git push -u gitee master

rem git remote add github git@github.com:accountbelongstox/GoGithub_plus.git
git branch -M "main"
git add .
git commit -m "new amend"
ssh -T git@github.com
git push -u github main
cmd


