__platform__=Windows
if [[ "Linux"  == "$(uname)" ]]; then
__platform__=Linux
#echo ===================
#echo ${BASH_SOURCE[0]}
#echo ======================
#/usr/bin/ls .
else
  __dir__=$(cd $(/usr/bin/dirname ${BASH_SOURCE[0]}); pwd )
  source /usr/etc/profile
  HOME=$USERPROFILE
  cd $__dir__/..

  if [ ! -z $1 ]; then
      WD=${__WD__/\\//}
      cd "$WD"
      $@
  fi
fi
