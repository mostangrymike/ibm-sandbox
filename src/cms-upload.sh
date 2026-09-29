#!/bin/bash
# Upload local NAME.TYPE files through the existing c3270 script port.
set -u

HOST=127.0.0.1
PORT=${CMS_SCRIPT_PORT:-3271}
FILEMODE=A
BUFFER=2048
MAXTRIES=3

action()
{
    printf '%s\n' "$1" | nc "$HOST" "$PORT"
}

upload()
{
    local input="$1"
    local directory localfile base cmsname cmstype result try status

    if [ ! -f "$input" ]; then
        echo "ERROR: file not found: $input" >&2
        return 1
    fi

    # c3270 may have been launched from a different working directory.
    # Resolve the local filename before passing it to Transfer().
    directory=$(cd "$(dirname "$input")" && pwd -P) || return 1
    base=$(basename "$input")
    localfile="$directory/$base"

    case "$base" in
        *.*)
            cmsname=${base%%.*}
            cmstype=${base#*.}
            ;;
        *)
            echo "ERROR: filename must be NAME.TYPE: $input" >&2
            return 1
            ;;
    esac

    cmsname=$(printf '%s' "$cmsname" | tr '[:lower:]' '[:upper:]')
    cmstype=$(printf '%s' "$cmstype" | tr '[:lower:]' '[:upper:]')

    if [ -z "$cmsname" ] || [ -z "$cmstype" ] ||
       [ ${#cmsname} -gt 8 ] || [ ${#cmstype} -gt 8 ]; then
        echo "ERROR: CMS name/type must be 1-8 characters: $cmsname $cmstype" >&2
        return 1
    fi

    # c3270 Transfer() treats quotes around LocalFile as literal pathname
    # characters. Keep the absolute path unquoted and reject action delimiters.
    case "$localfile" in
        *[,\"\\\(\)]*)
            echo "ERROR: unsupported punctuation in local path" >&2
            return 1
            ;;
    esac

    try=1
    while [ "$try" -le "$MAXTRIES" ]; do
        echo "=== $input -> $cmsname $cmstype $FILEMODE (attempt $try/$MAXTRIES) ==="

        result=$(action "Transfer(Direction=send,\"HostFile=$cmsname $cmstype $FILEMODE\",LocalFile=$localfile,Host=vm,Mode=ascii,Exist=replace,Recfm=fixed,Lrecl=80,BufferSize=$BUFFER)")
        status=$?
        printf '%s\n' "$result"

        # A successful c3270 action ends in an exact 'ok' status line.
        if [ "$status" -eq 0 ] &&
           [ "$(printf '%s\n' "$result" | tail -n 1)" = ok ]; then
            return 0
        fi

        if [ "$try" -lt "$MAXTRIES" ]; then
            echo "Transfer failed; recovering c3270 screen before retry..."
            action 'Clear()' >/dev/null
            sleep 2
        fi
        try=$((try + 1))
    done

    echo "ERROR: transfer failed after $MAXTRIES attempts: $input" >&2
    return 1
}

if [ "$#" -eq 0 ]; then
    echo "Usage: $0 file [file ...]" >&2
    echo "Example: $0 GITSEL.C GITREC.C GITCIDX.C" >&2
    exit 2
fi

for file in "$@"; do
    if ! upload "$file"; then
        echo
        echo "CMS upload FAILED."
        exit 1
    fi
done

echo
echo "CMS upload complete."
