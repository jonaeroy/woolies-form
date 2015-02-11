#!/bin/bash

dir_resolve()
{
    cd "$1" 2>/dev/null || return $?    # cd to desired directory; if fail, quell any error messages but return exit status
    echo "`pwd -P`" # output full, link-resolved path
}

dir=$( cd "$( dirname "$0" )" && pwd )
packages="`dir_resolve \"$dir/../../packages\"`"

echo $packages

echo ' --> Cleaning'

rm -rf "$packages/pytz" 2>/dev/null
rm $packages/gdata.zip $packages/atom.zip $packages/apiclient.zip $packages/wtforms.zip $packages/utils.zip $packages/protopigeon.zip 2>/dev/null

echo ' --> Starting Packaging'

echo ' --> Packaging pytz'
cd /tmp
rm -rf gae-pytz 2>/dev/null
hg clone https://code.google.com/p/gae-pytz/ gae-pytz
cp -r gae-pytz/pytz $packages

echo ' --> Packaging gdata'
cd /tmp
rm -rf gdata gdata.zip 2>/dev/null
hg clone https://code.google.com/p/gdata-python-client gdata
cd gdata/src
zip ../../gdata.zip -rq *
cd ../../
cp gdata.zip $packages

echo ' --> Packaging api-client'
sudo pip install --upgrade google-api-python-client
cd /tmp
rm -rf apiclient 2>/dev/null
mkdir apiclient
cd apiclient
echo "application: x\nversion: 1\nruntime: python27\napi_version: 1\n" > app.yaml
enable-app-engine-project .
rm app.yaml
zip ../apiclient.zip -rq *
cd ../
cp apiclient.zip $packages

echo ' --> Packaging wtforms & wtforms-json'
cd /tmp
rm -rf wtforms.zip wtforms wtforms-json 2>/dev/null

hg clone ssh://hg@bitbucket.org/simplecodes/wtforms wtforms
cd wtforms
hg checkout 1.0.4
zip ../wtforms.zip -rq wtforms AUTHORS.txt LICENSE.txt
cd ../

git clone https://github.com/kvesteri/wtforms-json.git wtforms-json
cd wtforms-json
zip -r ../wtforms.zip wtforms_json LICENSE
cd ../

cp wtforms.zip $packages

echo ' --> Packaging utils'
cd /tmp
mkdir utils
cd utils
wget https://micheles.googlecode.com/hg/decorator/src/decorator.py
wget https://gist.github.com/n1ywb/2570004/raw/77cad4d81a19d7a0fdbae3d1a7cec2682778efeb/retries.py
wget https://raw.github.com/jpvanhal/inflection/master/inflection.py
zip ../utils.zip decorator.py retries.py inflection.py
cd ../
cp utils.zip $packages


echo ' --> Packaging protopigeon'
cd /tmp
rm -rf protopigeon.zip protopigeon 2>/dev/null

git clone git@bitbucket.org:jonparrott/protopigeon.git protopigeon
cd protopigeon
zip ../protopigeon.zip -rq protopigeon license.txt
cd ../
cp protopigeon.zip $packages