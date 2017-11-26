Set-ExecutionPolicy RemoteSigned

$__file__ = $MyInvocation.MyCommand.Definition
$__dir__ = Split-Path -Parent $__file__
$__scripts__ = Split-Path -Parent $__dir__
$__cerberus__ = Split-Path -Parent $__scripts__

Function Quit
{
    Write-Host ""
    Write-Host $args
    Write-Host ""
	Write-Host press any key to exit setup
    Write-Host ""

	pause
	exit 100    
}

$config = $__cerberus__ + "\config.yaml"
$is_exits = Test-Path $config
if ( -not $is_exits ){
    Quit "config file :" $config  " NOT exists "
}

Function PythonCheck
{
    python --version
    if ( -not $? ){
        throw "Can not find python, please install it."        
    }

    pip --version
    if ( -not $? ){
        throw "Can not find python PIP , please install it."
    }#
    python -c "import yaml"
    if ( -not $? ){
        pip install pyyaml
        if ( -not $? ){
            throw install pyyaml failed.
        }
    }

}

Function Download
{
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

Function InstallMinGW
{
    $location = PyScript(
        "print installer.MinGWLocation(True);"
    )
    if(!$?){
        throw "read MinGW install package from config.yaml failed."
    }
    write-host $location "!!!!"
    $cache_dir = Join-Path $__cerberus__ 'cache'
    if ( ! (Test-Path $cache_dir) ) {
        md $cache_dir
    } 
    $tarball = Join-Path $cache_dir 'MinGW.zip'
    if( ! (Test-Path $tarball) ){
        Download $location  $tarball 
    }
    Expand-Archive -Path $tarball -DestinationPath $__cerberus__

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
    for($i=10;$i -gt 0;$i--)
    {
        sleep 1
        write-host exit $i "'s later ...." 
    }

    break

}

PythonCheck
InstallMinGW

$setup = (Join-Path $__dir__ 'installer.py')
$setup
if (!$?){
    exit 128
}

copy ( Join-Path $__cerberus__ "scripts\bash.cmd" ) ( Join-Path $__cerberus__ "bash.cmd" ) 
if (!$?){
    exit 129
}
write-host Install Successfully !!
exit 0
