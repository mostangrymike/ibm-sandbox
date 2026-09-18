#!/bin/bash
set -u

HOST=127.0.0.1
PORT=3271
BUFFER=2048
MAXTRIES=3

action()
{
    printf '%s\n' "$1" | nc "$HOST" "$PORT"
}

download()
{
    local cmsname="$1"
    local cmstype="$2"
    local filemode="${3:-A}"
    local localfile result try

    cmsname=$(printf '%s' "$cmsname" | tr '[:lower:]' '[:upper:]')
    cmstype=$(printf '%s' "$cmstype" | tr '[:lower:]' '[:upper:]')
    filemode=$(printf '%s' "$filemode" | tr '[:lower:]' '[:upper:]')

    if [ ${#cmsname} -gt 8 ] || [ ${#cmstype} -gt 8 ]; then
        echo "ERROR: CMS name/type exceeds 8 characters: $cmsname $cmstype" >&2
        return 1
    fi

    if [ ${#filemode} -ne 1 ]; then
        echo "ERROR: CMS filemode must be one character: $filemode" >&2
        return 1
    fi

    localfile="$cmsname.$cmstype"

    try=1
    while [ "$try" -le "$MAXTRIES" ]; do
        echo "=== $cmsname $cmstype $filemode -> $localfile (attempt $try/$MAXTRIES) ==="

        result=$(
            action "Transfer(Direction=receive,\"HostFile=$cmsname $cmstype $filemode\",LocalFile=$localfile,Host=vm,Mode=ascii,Exist=replace,BufferSize=$BUFFER)"
        )

        printf '%s\n' "$result"

        if printf '%s\n' "$result" | grep -q '^ok$'; then
            return 0
        fi

        echo "Transfer failed; recovering c3270 screen before retry..."

        action 'Clear()' >/dev/null
        sleep 2

        try=$((try + 1))
    done

    echo "ERROR: transfer failed after $MAXTRIES attempts: $cmsname $cmstype $filemode" >&2
    return 1
}

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
    echo "Usage: $0 NAME TYPE [FILEMODE]" >&2
    echo "Example: $0 ALLMACRO MACLIB T" >&2
    exit 2
fi

if ! download "$@"; then
    echo
    echo "CMS download FAILED."
    exit 1
fi

echo
echo "CMS download complete."
