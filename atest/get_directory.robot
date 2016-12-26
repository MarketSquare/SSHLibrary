*** Settings ***
Force Tags      pybot   jybot
Resource        resources/sftp.robot
Suite Setup     Login and Upload Test Files
Suite Teardown  Remove Test Files And Close Connections
Library         OperatingSystem  WITH NAME  OS

*** Test Cases ***
Get Directory To Existing Local Path
    [Setup]  Create Directory  ${LOCAL TMPDIR}
    Get Directory  ${REMOTE TEST ROOT}  ${LOCAL TMPDIR}
    Directory Should Exist With Content  ${LOCAL TMPDIR}
    [Teardown]  Remove Directory  ${LOCAL TMPDIR}  recursive=True

Get Directory To Non-Existing Local Path
    [Setup]  OS.Directory Should Not Exist  .${/}tmpdir
    SSH.Get Directory  ${REMOTE TEST ROOT}/  .${/}tmpdir
    Directory Should Exist With Content  .${/}tmpdir
    [Teardown]  Remove Directory  .${/}tmpdir  recursive=True

Get Directory Including Subdirectories To Existing Local Path
    [Setup]  Create Directory  ${LOCAL TMPDIR}
    Get Directory  ${REMOTE TEST ROOT}  ${LOCAL TMPDIR}  recursive=True
    Directory Should Exist Including Subdirectories  ${LOCAL TMPDIR}
    [Teardown]  Remove Directory  ${LOCAL TMPDIR}  recursive=True

Get Directory Including Subdirectories To Non-Existing Local Path
    [Setup]  OS.Directory Should Not Exist  my
    Get Directory  ${REMOTE TEST ROOT}  my${/}own${/}tmpdir  recursive=True
    Directory Should Exist Including Subdirectories  my${/}own${/}tmpdir
    [Teardown]  Remove Directory  my  recursive=True

Get Directory Including Empty Subdirectories
    [Setup]  Create Directory  ${LOCAL TMPDIR}
    Execute Command  mkdir ${REMOTE TEST ROOT}/empty
    Get Directory  ${REMOTE TEST ROOT}  ${LOCAL TMPDIR}  recursive=True
    OS.Directory Should Exist  ${LOCAL TMPDIR}/empty
    Directory Should Exist Including Subdirectories  ${LOCAL TMPDIR}
    [Teardown]  Remove Directory  ${LOCAL TMPDIR}  recursive=True

Get Directory Using Relative Source
    [Setup]  OS.Directory Should Not Exist  my
    Get Directory  ${REMOTE TEST ROOT NAME}  my
    Directory Should Exist With Content  my
    [Teardown]  Remove Directory  my  recursive=True

Get Directory Should Fail When Source Does Not Exists
    Run Keyword And Expect Error  There was no directory matching 'non-existing'.
    ...                           SSH.Get Directory  non-existing  /tmp

Get Directory overrrides existing files
    [Setup]  Create Directory  ${LOCAL TMPDIR}
    Create File   ${LOCAL TMPDIR}${/}${TEST FILE NAME}    foo
    Get Directory  ${REMOTE TEST ROOT}  ${LOCAL TMPDIR}  recursive=True
    Directory Should Exist Including Subdirectories  ${LOCAL TMPDIR}
    File content should be   ${LOCAL TMPDIR}${/}${TEST FILE NAME}    This is a test file.\n
    [Teardown]  Remove Directory  ${LOCAL TMPDIR}  recursive=True

Get Directory works if there are existing local directories
    [Setup]  Create Directory  ${LOCAL TMPDIR}
    Create directory   ${LOCAL TMPDIR}${/}${SUBDIRECTORY NAME}${/}${DIRECTORY WITH EMPTY SUBDIRECTORY}${/}${EMPTY SUB DIR}
    Get Directory  ${REMOTE TEST ROOT}  ${LOCAL TMPDIR}  recursive=True
    Directory Should Exist Including Subdirectories  ${LOCAL TMPDIR}
    [Teardown]  Remove Directory  ${LOCAL TMPDIR}  recursive=True

*** Keywords ***
File content should be
    [Arguments]    ${file}    ${expected}
    ${actual}=     OS.Get file    ${file}
    Should be equal    ${actual}    ${expected}

Directory Should Exist With Content
    [Arguments]  ${destination}
    OS.File Should Exist  ${destination}${/}${TEST FILE NAME}
    OS.File Should Exist  ${destination}${/}${FILE WITH NEWLINES NAME}
    OS.File Should Exist  ${destination}${/}${FILE WITH SPECIAL CHARS NAME}
    OS.File Should Not Exist  ${destination}${/}${SUBDIRECTORY NAME}
    OS.Directory Should Not Exist  ${destination}${/}${SUBDIRECTORY NAME}

Directory Should Exist Including Subdirectories
    [Arguments]  ${destination}
    OS.File Should Exist  ${destination}${/}${TEST FILE NAME}
    OS.File Should Exist  ${destination}${/}${FILE WITH NEWLINES NAME}
    OS.File Should Exist  ${destination}${/}${FILE WITH SPECIAL CHARS NAME}
    OS.File Should Exist  ${destination}${/}${SUBDIRECTORY NAME}${/}${FILE WITH NON-ASCII NAME}
    OS.Directory Should Exist  ${destination}${/}${SUBDIRECTORY NAME}${/}${DIRECTORY WITH EMPTY SUBDIRECTORY}${/}${EMPTY SUB DIR}