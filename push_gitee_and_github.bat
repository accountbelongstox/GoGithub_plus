git add .
git branch -M "master"
git commit -m "new amend"
git remote add gitee git@gitee.com:accountbelongstox/GoGitHub_plus.git
git push -u gitee master --force
git remote add github git@github.com:accountbelongstox/GoGithub_plus.git
git branch -M "main"
git commit -m "new amend"
git push -u github main --force
cmd