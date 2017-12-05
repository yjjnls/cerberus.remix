Set-ExecutionPolicy RemoteSigned

$__file__ = $MyInvocation.MyCommand.Definition
$__dir__ = Split-Path -Parent $__file__
$__scripts__ = Split-Path -Parent $__dir__
$__cerberus__ = Split-Path -Parent $__scripts__



$config = $__cerberus__ + "\config.yaml"
$is_exits = Test-Path $config
if ( -not $is_exits ){
    Write-Host "config file :" $config  " NOT exists "
    exit 1
}

Function Download
{
    write-host download $args[0] to $args[1]
    $client=new-object System.Net.WebClient
    $client.DownloadFile( $args[0], $args[1] )
    if( !$?){
        throw "Download Filed ! "
    }
}



Function PyScript
{
    $code = -Join( "import sys; sys.path.insert(0,r'",$__dir__,"');import installer;")

    For($i=0;$i -lt $args.Count; $i++)
    {
        $code = $code + $args[$i]
        #$code = -Join( $code , $args[$i] )
    }
    python -c $code
}


Function PythonCheck
{
    python --version
    if ( -not $? ){
        throw "Can not find python, please install it."        
    }

    python -c "import yaml"
    if ( -not $? ){ 
        git clone https://github.com/yaml/pyyaml.git -b 3.12 pyyaml
        cd pyyaml
        python setup.py install
        if ( -not $? ){
            throw "Install pyyaml failed."
        }
    }
}

Function InstallMinGW
{
    $location = PyScript(
        "print installer.MinGWLocation(True);"
    )
    if(!$?){
        throw "read MinGW install package from config.yaml failed."
    }

    $cache_dir = Join-Path $__cerberus__ 'cache'
    if ( ! (Test-Path $cache_dir) ) {
        md $cache_dir
    } 
    $tarball = Join-Path $cache_dir 'MinGW.zip'
    if( ! (Test-Path $tarball) ){
        Download $location  $tarball 
    }

    $code  ="import zipfile;f=zipfile.ZipFile(r'" + $tarball + "','r');"
    $code +="f.extractall(r'" + $__cerberus__ +"');"
    python -c $code
    if ( -not $? ){
        throw "extract MinGW.zip failed"
    }

    $execFile = (Join-Path $__cerberus__ "MinGW\bin\mingw-get.exe")

    &$execFile install msys-base
    &$execFile install msys-wget
    &$execFile install msys-flex
    &$execFile install msys-bison
    &$execFile install msys-perl

    if ( !$?){
        throw 'MinGW setup or component install failed.'
    }


}
   #==============================#
   #           Main               #
   #==============================#
   


Trap {

    Write-Host `n `n 'Installation failed!' `n

    write-host $_.exception.message `n`n
    write-host ''
	break

    exit 128 #break

}

PythonCheck
InstallMinGW

write-host MinGW Install Successfully !!
exit 0
