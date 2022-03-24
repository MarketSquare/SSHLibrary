*** Settings ***
Default Tags      pybot   jybot
Resource        resources/sftp.robot
Suite Setup     Login and Upload Test Files
Suite Teardown  Remove Test Files And Close Connections
Library         OperatingSystem  WITH NAME  OS
Library         DateTime

*** Test Cases ***
Get Directory To Existing Local Path
    [Setup]  Create Directory  ${LOCAL TMPDIR}
    Get Directory  ${REMOTE TEST ROOT}  ${LOCAL TMPDIR}
    Directory Should Exist With Content  ${LOCAL TMPDIR}  ${/}robot-testdir
    [Teardown]  Remove Directory  ${LOCAL TMPDIR}  recursive=True

Get Directory To Existing Local Path With SCP (transfer)
    [Setup]  Create Directory  ${LOCAL TMPDIR}
    Get Directory  ${REMOTE TEST ROOT}  ${LOCAL TMPDIR}  scp=TRANSFER
    Directory Should Exist With Content  ${LOCAL TMPDIR}  ${/}robot-testdir
    [Teardown]  Remove Directory  ${LOCAL TMPDIR}  recursive=True

Get Directory To Existing Local Path With SCP (all)
    [Tags]  pybot
    [Setup]  Create Directory  ${LOCAL TMPDIR}
    Get Directory  ${REMOTE TEST ROOT}  ${LOCAL TMPDIR}  scp=ALL
    Directory Should Exist Including Subdirectories  ${LOCAL TMPDIR}  ${/}robot-testdir
    [Teardown]  Remove Directory  ${LOCAL TMPDIR}  recursive=True

Get Directory To Non-Existing Local Path
    [Setup]  OS.Directory Should Not Exist  .${/}tmpdir
    SSH.Get Directory  ${REMOTE TEST ROOT}/  .${/}tmpdir
    Directory Should Exist With Content  .${/}tmpdir
    [Teardown]  Remove Directory  .${/}tmpdir  recursive=True

Get Directory Including Subdirectories To Existing Local Path
    [Setup]  Create Directory  ${LOCAL TMPDIR}
    Get Directory  ${REMOTE TEST ROOT}  ${LOCAL TMPDIR}  recursive=True
    Directory Should Exist Including Subdirectories  ${LOCAL TMPDIR}  ${/}robot-testdir
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
    OS.Directory Should Exist  ${LOCAL TMPDIR}/robot-testdir/empty
    Directory Should Exist Including Subdirectories  ${LOCAL TMPDIR}  ${/}robot-testdir
    [Teardown]  Remove Directory  ${LOCAL TMPDIR}  recursive=True

Get Directory With Square Brackets In Name
    [Setup]  Create Directory  ${LOCAL TMPDIR}
    Execute Command  mkdir ${REMOTE TEST ROOT}/directory[1]
    Get Directory  ${REMOTE TEST ROOT}  ${LOCAL TMPDIR}  recursive=True
    OS.Directory Should Exist  ${LOCAL TMPDIR}${/}robot-testdir/directory[1]
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
    Directory Should Exist Including Subdirectories  ${LOCAL TMPDIR}  ${/}robot-testdir
    File content should be   ${LOCAL TMPDIR}${/}robot-testdir${/}${TEST FILE NAME}    This is a test file.\n
    [Teardown]  Remove Directory  ${LOCAL TMPDIR}  recursive=True

Get Directory works if there are existing local directories
    [Setup]  Create Directory  ${LOCAL TMPDIR}
    Create directory   ${LOCAL TMPDIR}${/}${SUBDIRECTORY NAME}${/}${DIRECTORY WITH EMPTY SUBDIRECTORY}${/}${EMPTY SUB DIR}
    Get Directory  ${REMOTE TEST ROOT}  ${LOCAL TMPDIR}  recursive=True
    Directory Should Exist Including Subdirectories  ${LOCAL TMPDIR}  ${/}robot-testdir
    [Teardown]  Remove Directory  ${LOCAL TMPDIR}  recursive=True

Get Directory containing a symlink
   [Setup]  Create Directory  ${LOCAL TMPDIR}
   Execute Command  mkdir ${REMOTE TEST ROOT}/symlink
   Execute Command  cd ${REMOTE TEST ROOT}/symlink; ln -s ../${TEST FILE NAME} ${SYMLINK TO TEST FILE}
   Get Directory  ${REMOTE TEST ROOT}/symlink  ${LOCAL TMPDIR}
   OS.File Should Exist  ${LOCAL TMPDIR}${/}symlink${/}${SYMLINK TO TEST FILE}
   [Teardown]  Remove Directory  ${LOCAL TMPDIR}  recursive=True

Get Directory With SCP (transfer) And Preserve Time
    [Tags]  pybot
    [Setup]  Create Directory  ${LOCAL TMPDIR}
    Sleep  15s
    ${current_time} =  Get Current Date  result_format=epoch  exclude_millis=False
    Get Directory  ${REMOTE TEST ROOT}  ${LOCAL TMPDIR}  scp=TRANSFER  scp_preserve_times=True
    Directory Should Exist With Content  ${LOCAL TMPDIR}  ${/}robot-testdir
    ${last_access_time} =  Run  stat -c %X ${LOCAL TMPDIR}${/}robot-testdir/test_file.txt
    ${last_modify_time} =  Run  stat -c %X ${LOCAL TMPDIR}${/}robot-testdir/test_file.txt
    Should Be True  ${current_time} > ${last_access_time}
    Should Be True  ${current_time} > ${last_modify_time}
    [Teardown]  Remove Directory  ${LOCAL TMPDIR}  recursive=True

Get Directory With SCP (all) And Preserve Time
    [Tags]  pybot
    [Setup]  Create Directory  ${LOCAL TMPDIR}
    Sleep  15s
    ${current_time} =  Get Current Date  result_format=epoch  exclude_millis=False
    Get Directory  ${REMOTE TEST ROOT}  ${LOCAL TMPDIR}  scp=ALL  scp_preserve_times=True
    Directory Should Exist Including Subdirectories  ${LOCAL TMPDIR}  ${/}robot-testdir
    ${last_access_time} =  Run  stat -c %X ${LOCAL TMPDIR}${/}robot-testdir
    ${last_modify_time} =  Run  stat -c %X ${LOCAL TMPDIR}${/}robot-testdir
    Should Be True  ${current_time} > ${last_access_time}
    Should Be True  ${current_time} > ${last_modify_time}
    [Teardown]  Remove Directory  ${LOCAL TMPDIR}  recursive=True

*** Keywords ***
File content should be
    [Arguments]    ${file}    ${expected}
    ${actual}=     OS.Get file    ${file}
    Should be equal    ${actual}    ${expected}

Directory Should Exist With Content
    [Arguments]  ${destination}  ${parent_folder}=${EMPTY}
    OS.File Should Exist  ${destination}${parent_folder}${/}${TEST FILE NAME}
    OS.File Should Exist  ${destination}${parent_folder}${/}${FILE WITH NEWLINES NAME}
    OS.File Should Exist  ${destination}${parent_folder}${/}${FILE WITH SPECIAL CHARS NAME}
    OS.File Should Exist  ${destination}${parent_folder}${/}${FILE WITH SQUARE BRACKETS NAME}
    OS.File Should Not Exist  ${destination}${parent_folder}${/}${SUBDIRECTORY NAME}
    OS.Directory Should Not Exist  ${destination}${parent_folder}${/}${SUBDIRECTORY NAME}

Directory Should Exist Including Subdirectories
    [Arguments]  ${destination}  ${parent_folder}=${EMPTY}
    OS.File Should Exist  ${destination}${parent_folder}${/}${TEST FILE NAME}
    OS.File Should Exist  ${destination}${parent_folder}${/}${FILE WITH NEWLINES NAME}
    OS.File Should Exist  ${destination}${parent_folder}${/}${FILE WITH SPECIAL CHARS NAME}
    OS.File Should Exist  ${destination}${parent_folder}${/}${SUBDIRECTORY NAME}${/}${FILE WITH NON-ASCII NAME}
    OS.Directory Should Exist  ${destination}${parent_folder}${/}${SUBDIRECTORY NAME}${/}${DIRECTORY WITH EMPTY SUBDIRECTORY}${/}${EMPTY SUB DIR}
