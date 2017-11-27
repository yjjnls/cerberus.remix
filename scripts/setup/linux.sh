__dir__=$(cd $(/usr/bin/dirname ${BASH_SOURCE[0]}); pwd )

python -c "import yaml"
if [ $? -ne 0 ]; then
   version=3.12
   wget https://github.com/yaml/pyyaml/archive/${version}.tar.gz &&
   tar -vxf ${version}.tar.gz &&
   cd pyyaml-${version} &&
   python setup.py install
   if [ $? -ne 0 ]; then
      echo install pyyaml failed!
      exit 10
   fi
fi
