*** Settings ***
Force Tags      pybot   jybot
Resource        resources/sftp.robot
Suite Setup     Login and Upload Test Files
Suite Teardown  Remove Test Files And Close Connections
Test Teardown   Remove Directory  ${LOCAL TMPDIR}  yes
Library         OperatingSystem  WITH NAME  OS

*** Test Cases ***
Get File Using Absolute Source
    SSH.Get File  ${REMOTE TEST ROOT}/${SUBDIRECTORY NAME}/${FILE WITH NON-ASCII NAME}  ${LOCAL TMPDIR}${/}
    OS.File Should Exist  ${LOCAL TMPDIR}${/}${FILE WITH NON-ASCII NAME}
    [Teardown]  OS.Remove File  ${LOCAL TMPDIR}${/}${FILE WITH NON-ASCII NAME}

Get File Using Absolute Windows Source
    [tags]   windows
    SSH.Get File  ${REMOTE WINDOWS TEST ROOT}/${SUBDIRECTORY NAME}/${FILE WITH NON-ASCII NAME}  ${LOCAL TMPDIR}${/}
    OS.File Should Exist  ${LOCAL TMPDIR}${/}${FILE WITH NON-ASCII NAME}
    [Teardown]  OS.Remove File  ${LOCAL TMPDIR}${/}${FILE WITH NON-ASCII NAME}

Get File Using Relative Source
    SSH.Get File  ${REMOTE TEST ROOT NAME}/${SUBDIRECTORY NAME}/${FILE WITH NON-ASCII NAME}  ${TEST FILE NAME}
    OS.File Should Exist  ${TEST FILE NAME}
    [Teardown]  OS.Remove File  ${TEST FILE NAME}

Get File Using Pattern As Source
    @{expected} =  Create List  ${TEST FILE NAME}
    ...                         ${FILE WITH NEWLINES NAME}
    ${destination} =  Set Variable  ${LOCAL TMPDIR}${/}
    SSH.Get File  ${REMOTE TEST ROOT}/*est*.txt  ${destination}
    : FOR  ${filename}  IN  @{expected}
    \  OS.File Should Exist  ${destination}${/}${filename}

Get File From Path Not Under Remote Home
    [Setup]  Create Tmp Dir And Move File
    SSH.Get File  /tmp/test_file.txt  ${LOCAL TMPDIR}${/}
    OS.File Should Exist  ${LOCAL TMPDIR}${/}test_file.txt
    [Teardown]  Remove Tmp Dir And Remote File

Get File With Multiple Sources To Single File Fails
    Run Keyword And Expect Error
    ...  Cannot copy multiple source files to one destination file.
    ...  SSH.Get File  ${REMOTE TEST ROOT}/*.txt  ${LOCAL TMPDIR}${/}foo

Get File To Different Name
    ${new name} =  Set Variable  foo.txt
    SSH.Get File  ${REMOTE TEST ROOT}/${SUBDIRECTORY NAME}/${FILE WITH NON-ASCII NAME}  ${new name}
    OS.File Should Exist  ${new name}
    [Teardown]  OS.Remove File  ${new name}

Get File To Current Working Directory
    SSH.Get File  ${REMOTE TEST ROOT}/${SUBDIRECTORY NAME}/${FILE WITH NON-ASCII NAME}  .
    OS.File Should Exist  ${FILE WITH NON-ASCII NAME}
    [Teardown]  OS.Remove File  ${FILE WITH NON-ASCII NAME}

Get File When Destination Path Does Not Exist
    ${target} =  Set Variable  ${LOCAL TMPDIR}/new/none.txt
    SSH.Get File  ${REMOTE TEST ROOT}/${TEST FILE NAME}  ${target}
    OS.File Should Exist  ${target}
    [Teardown]  OS.Remove File  ${target}

Get File Should Fail When There Are No Source Files
    Run Keyword And Expect Error
    ...  There were no source files matching 'non-existing'.
    ...  SSH.Get File  non-existing

*** Keywords ***
Create Tmp Dir And Move File
    Put File  ${TEST FILE}  /tmp/
    Create Directory  ${LOCAL TMPDIR}

Remove Tmp Dir And Remote File
    Execute Command  rm -f /tmp/test_file.txt
    Remove Directory  ${LOCAL TMPDIR}  yes
