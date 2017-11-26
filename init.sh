#if [ "x$MSYSTEM" == "xmsys" ]; then
#echo ===================
#echo ${BASH_SOURCE[0]}
#echo ======================
#/usr/bin/ls .
__dir__=$(cd $(/usr/bin/dirname ${BASH_SOURCE[0]}); pwd )
source /usr/etc/profile
HOME=$USERPROFILE
cd $__dir__

#else


#echo Linux System

#fi

