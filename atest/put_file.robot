*** Settings ***
Force Tags      pybot   jybot
Resource        resources/sftp.robot
Suite Setup     Login As Valid User
Suite Teardown  Close All Connections
Library         OperatingSystem  WITH NAME  OS
Library         String
Library         DateTime

*** Test Cases ***
Put File To Absolute Destination
    SSH.File Should Not Exist  ${REMOTE TEST ROOT}/${FILE WITH NON-ASCII NAME}
    Put File  ${FILE WITH NON-ASCII}  ${REMOTE TEST ROOT}/
    SSH.File Should Exist  ${REMOTE TEST ROOT}/${FILE WITH NON-ASCII NAME}
    [Teardown]  Execute Command  rm -rf ${REMOTE TEST ROOT}

Put File To Absolute Destination With SCP (transfer)
    SSH.File Should Not Exist  ${REMOTE TEST ROOT}/${TEST FILE NAME}
    Put File  ${TEST FILE}  ${REMOTE TEST ROOT}/  scp=TRANSFER
    SSH.File Should Exist  ${REMOTE TEST ROOT}/${TEST FILE NAME}
    [Teardown]  Execute Command  rm -rf ${REMOTE TEST ROOT}

Put File To Absolute Destination With SCP (all)
    SSH.File Should Not Exist  ${REMOTE TEST ROOT}/${TEST FILE NAME}
    Execute Command  mkdir ${REMOTE TEST ROOT NAME}
    Put File  ${TEST FILE}  ${REMOTE TEST ROOT}/  scp=ALL
    SSH.File Should Exist  ${REMOTE TEST ROOT}/${TEST FILE NAME}
    [Teardown]  Execute Command  rm -rf ${REMOTE TEST ROOT}

Put File To Absolute Destination With Intermediate Subdirectories
    SSH.File Should Not Exist  ${REMOTE TEST ROOT}/robotdir/${FILE WITH NON-ASCII NAME}
    Put File  ${FILE WITH NON-ASCII}  ${REMOTE TEST ROOT}/robotdir/
    SSH.File Should Exist  ${REMOTE TEST ROOT}/robotdir/${FILE WITH NON-ASCII NAME}
    [Teardown]  Execute Command  rm -rf ${REMOTE TEST ROOT}

Put File To Relative Destination
    SSH.File Should Not Exist  foo.txt
    Put File  ${FILE WITH NON-ASCII}  foo.txt
    SSH.File Should Exist  foo.txt
    [Teardown]  Execute Command  rm -f foo.txt

Put File To Relative Destination With Intermediate Subdirectories
    SSH.File Should Not Exist  robotdir/${FILE WITH NON-ASCII NAME}
    Put File  ${FILE WITH NON-ASCII}  robotdir/
    SSH.File Should Exist  robotdir/${FILE WITH NON-ASCII NAME}
    [Teardown]  Execute Command  rm -rf robotdir

Put File To Existing Directory Without Trailing Path Separator
    SSH.Directory Should Not Exist  robotdir
    Execute Command    mkdir robotdir
    Put File  ${FILE WITH NON-ASCII}  robotdir
    SSH.File Should Exist  robotdir/${FILE WITH NON-ASCII NAME}
    [Teardown]  Execute Command  rm -rf robotdir

Put File With Square Brackets
    SSH.File Should Not Exist  ${FILE WITH SQUARE BRACKETS NAME}
    Put File  ${FILE WITH SQUARE BRACKETS}  robotdir/
    SSH.File Should Exist  robotdir/${FILE WITH SQUARE BRACKETS NAME}
    [Teardown]  Execute Command  rm -rf robotdir

Put File To Home Directory
    SSH.File Should Not Exist  ${FILE WITH NON-ASCII NAME}
    Put File  ${FILE WITH NON-ASCII}  .
    SSH.File Should Exist  ${FILE WITH NON-ASCII NAME}
    [Teardown]  Execute Command  rm -f ${FILE WITH NON-ASCII NAME}

Put File With Special Characters In Filename
    [Documentation]  http://code.google.com/p/robotframework-sshlibrary/issues/detail?id=55
    ${target} =  Set Variable  ${FILE WITH SPECIAL CHARS NAME}
    SSH.File Should Not Exist  ${target}
    Put File  ${FILE WITH SPECIAL CHARS}  ${target}
    SSH.File Should Exist  ${target}
    [Teardown]  Execute Command  rm -f ${target}

Put File Should Fail When There Are No Source Files
    Run Keyword And Expect Error  There are no source files matching 'nonexisting'.
    ...                           SSH.Put File  nonexisting

Put File And Specify Remote Newlines
    [Setup]  Create Directory  ${LOCAL TMPDIR}
    ${target} =  Set Variable  ${FILE WITH NEWLINES NAME}
    SSH.File Should Not Exist  ${target}
    Put File  ${FILE WITH NEWLINES}  ${target}  newline=CRLF
    SSH.File Should Exist  ${target}
    ${expected} =  OS.Get Binary File  ${FILE WITH NEWLINES}
    SSH.Get File  ${target}  ${LOCAL TMPDIR}${/}
    ${content}=  OS.Get Binary File  ${LOCAL TMPDIR}${/}${FILE WITH NEWLINES NAME}
    ${win_rn}=   Encode String To Bytes  \r\n  UTF-8
    ${linux_n}=   Encode String To Bytes  ${\n}  UTF-8
    ${content}=  Replace String  ${content}  ${win_rn}  ${linux_n}
    Should Be Equal  ${content}  ${expected}
    [Teardown]  Remove Local Temp Dir And Remote File  ${target}

Put File With Pattern In Source File Name
    SSH.File Should Not Exist  ${REMOTE TEST ROOT}/${TEST FILE NAME}
    SSH.File Should Not Exist  ${REMOTE TEST ROOT}/${FILE WITH NEWLINES NAME}
    Put File  ${LOCAL TEXTFILES}${/}?est*.txt  ${REMOTE TEST ROOT}/
    SSH.File Should Exist  ${REMOTE TEST ROOT}/${TEST FILE NAME}
    SSH.File Should Exist  ${REMOTE TEST ROOT}/${FILE WITH NEWLINES NAME}
    [Teardown]  Execute Command  rm -rf ${REMOTE TEST ROOT}

Put File With Pattern In Source Directory Name
    SSH.File Should Not Exist  ${REMOTE TEST ROOT}/${TEST FILE NAME}
    Put File  ${LOCAL TEST DATA}${/}text*es${/}${TEST FILE NAME}  ${REMOTE TEST ROOT}/
    SSH.File Should Exist  ${REMOTE TEST ROOT}/${TEST FILE NAME}
    [Teardown]  Execute Command  rm -rf ${REMOTE TEST ROOT}

Putting Multiple Source Files To Single File Fails
    Run Keyword And Expect Error  ValueError: It is not possible to copy multiple source files to one destination file.
    ...                           Put File  ${LOCAL TEXTFILES}${/}?est*.txt  invalid.txt

Put File Overwrite If User In The Same Group
   Put File  ${LOCAL TEXTFILES}${/}${TEST FILE NAME}
   SSH.File Should Exist  ${TEST FILE NAME}
   Add testkey User To Group test And Set Permissions
   Change User And Overwrite File
   Switch Connection  1
   SSH.File Should Exist  ${TEST FILE NAME}
   [Teardown]  Remove testkey User From Group test And Cleanup

Put File And Check For Proper Permissions
    [Tags]  linux
	Put File  ${LOCAL TEXTFILES}${/}${TEST FILE NAME}  ${REMOTE TEST ROOT}/  mode=0755
	${output}=  Execute Command   ls
	Should Contain  ${output}  to_put
	Check File Permissions    0755    ${REMOTE_TEST_ROOT}${/}${TEST FILE NAME}
	[Teardown]  Execute Command  rm -rf ${REMOTE TEST ROOT}

Put File With Scp (all) And Preserve Time
    SSH.File Should Not Exist  ${REMOTE TEST ROOT}/${TEST FILE NAME}
    Execute Command  mkdir ${REMOTE TEST ROOT NAME}
    ${current_time} =  Get Current Date  result_format=epoch  exclude_millis=True
    Put File  ${TEST FILE}  ${REMOTE TEST ROOT}/  scp=ALL  scp_preserve_times=True
    SSH.File Should Exist  ${REMOTE TEST ROOT}/${TEST FILE NAME}
    ${last_access_time} =  Execute Command  stat -c %X ${REMOTE TEST ROOT}/${TEST FILE NAME}
    ${last_modify_time} =  Execute Command  stat -c %X ${REMOTE TEST ROOT}/${TEST FILE NAME}
    Should Be True  ${current_time} > ${last_access_time}
    Should Be True  ${current_time} > ${last_modify_time}
    [Teardown]  Execute Command  rm -rf ${REMOTE TEST ROOT}

Put File With SCP (transfer) And Preserve Time
    SSH.File Should Not Exist  ${REMOTE TEST ROOT}/${TEST FILE NAME}
    Execute Command  mkdir ${REMOTE TEST ROOT NAME}
    ${current_time} =  Get Current Date  result_format=epoch  exclude_millis=True
    Put File  ${TEST FILE}  ${REMOTE TEST ROOT}/  scp=TRANSFER  scp_preserve_times=True
    SSH.File Should Exist  ${REMOTE TEST ROOT}/${TEST FILE NAME}
    ${last_access_time} =  Execute Command  stat -c %X ${REMOTE TEST ROOT}/${TEST FILE NAME}
    ${last_modify_time} =  Execute Command  stat -c %X ${REMOTE TEST ROOT}/${TEST FILE NAME}
    Should Be True  ${current_time} > ${last_access_time}
    Should Be True  ${current_time} > ${last_modify_time}
    [Teardown]  Execute Command  rm -rf ${REMOTE TEST ROOT}

*** Keywords ***
Change User And Overwrite File
    Open Connection  ${HOST}  prompt=${PROMPT}
    Login With Public Key  ${KEY USERNAME}  ${KEY}
    Put File  ${LOCAL TEXTFILES}${/}${TEST FILE NAME}  ${REMOTE HOME TEST}
    [Teardown]  Close Connection

Add testkey User To Group test And Set Permissions
    Execute Command  usermod -a -G test testkey  sudo=True  sudo_password=test
    Execute Command  chmod -R 660 ${TEST FILE NAME}

Remove testkey User From Group test And Cleanup
    Execute Command  gpasswd -d testkey test  sudo=True  sudo_password=test
    Execute Command  rm -rf ${TEST FILE NAME}

Remove Local Temp Dir And Remote File
    [Arguments]  ${path}
    Remove Directory  ${LOCAL TMPDIR}  yes
    Execute Command  rm -f ${path}
