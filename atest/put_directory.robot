*** Settings ***
Default Tags    pybot   jybot
Resource        resources/sftp.robot
Suite Setup     Login As Valid User
Suite Teardown  Close All Connections
Library         OperatingSystem  WITH NAME  OS
Library         Collections
Library         DateTime

*** Test Cases ***
Put Directory To Existing Remote Path
    [Setup]  SSH.Directory Should Not Exist  textfiles
    Put Directory  ${LOCAL TEXTFILES}  .
    Remote Directory Should Exist With Content  ./textfiles
    [Teardown]  Execute Command  rm -rf ./textfiles

Put Directory To Non-Existing Remote Path
    [Setup]  SSH.Directory Should Not Exist  another_dir_name
    Put Directory  ${LOCAL TEXTFILES}  another_dir_name
    Remote Directory Should Exist With Content  another_dir_name
    [Teardown]  Execute Command  rm -rf another_dir_name

Put Directory Including Subdirectories To Existing Remote Path
    Put Directory  ${LOCAL TEXTFILES}  .  recursive=True
    Remote Directory Should Exist With Subdirectories  ./textfiles
    [Teardown]  Execute Command  rm -rf ./textfiles

Put Directory Including Subdirectories To Existing Remote Path With SCP (transfer)
    Put Directory  ${LOCAL TEXTFILES}  .  recursive=True  scp=TRANSFER
    Remote Directory Should Exist With Subdirectories  ./textfiles
    [Teardown]  Execute Command  rm -rf ./textfiles

Put Directory Including Subdirectories To Existing Remote Path With SCP (all)
    [Tags]  pybot
    Put Directory  ${LOCAL TEXTFILES}  .  recursive=True  scp=ALL
    Remote Directory Should Exist With Subdirectories  ./textfiles
    [Teardown]  Execute Command  rm -rf ./textfiles

Put Directory Including Subdirectories To Non-Existing Remote Path
    [Setup]  SSH.Directory Should Not Exist  another/dir/path
    Put Directory  ${LOCAL TEXTFILES}  another/dir/path  recursive=True
    Remote Directory Should Exist With Subdirectories  another/dir/path
    [Teardown]  Execute Command  rm -rf another

Put Directory Including Empty Subdirectories
    [Setup]  OS.Create Directory  ${LOCAL TEXTFILES}${/}empty
    Put Directory  ${LOCAL TEXTFILES}  .  recursive=True
    SSH.Directory Should Exist  textfiles/empty
    Remote Directory Should Exist With Subdirectories  textfiles
    [Teardown]  Remove Local Empty Directory And Remote Files

Put Directory With Square Brackets In Name
    [Setup]  OS.Create Directory  ${LOCAL TEXTFILES}${/}directory[1]
    Put Directory  ${LOCAL TEXTFILES}  .  recursive=True
    SSH.Directory Should Exist  textfiles/directory[1]
    [Teardown]  Remove Local And Remote Directory With Square Brackets

Put Directory Using Relative Source
    [Setup]  SSH.Directory Should Not Exist  ${REMOTE TEST ROOT}
    Put Directory  ${CURDIR}${/}testdata${/}textfiles  ${REMOTE TEST ROOT}
    Remote Directory Should Exist With Content  ${REMOTE TEST ROOT}
    [Teardown]  Execute Command  rm -rf ${REMOTE TEST ROOT}

Put Directory Should Fail When Source Does Not Exists
    Run Keyword And Expect Error  There was no source path matching 'non-existing'.
    ...                           Put Directory  non-existing

Put Directory Containing A File With Colon In Its Name
     [Tags]  linux
     [Setup]  SSH.Directory Should Not Exist  ${REMOTE TEST ROOT}
     Create File With Colon Char In Its Name
     Put Directory  ${CURDIR}${/}testdata${/}textfiles  ${REMOTE TEST ROOT}
     Check And Remove Local Added Directory   ${REMOTE TEST ROOT}
     [Teardown]  Execute Command  rm -rf ${REMOTE TEST ROOT}

Put Directory And Check For Proper Permissions
    [Tags]  linux
	Put Directory  ${CURDIR}${/}testdata${/}to_put  recursive=True  mode=0755
	${output}=  Execute Command   ls
	Should Contain  ${output}  to_put
	Check File Permissions    0755    to_put${/}ExampleText3.txt
	Check Folder Permissions    0755
	[Teardown]  Execute Command  rm -rf ${CURDIR}${/}testdata${/}to_put

Put Directory With SCP (transfer) And Preserve Time
    ${current_time} =  Get Current Date  result_format=epoch  exclude_millis=True
    Put Directory  ${LOCAL TEXTFILES}  .  recursive=True  scp=TRANSFER  scp_preserve_times=True
    Remote Directory Should Exist With Subdirectories  ./textfiles
    ${last_access_time} =  Execute Command  stat -c %X ./textfiles/test_file.txt
    ${last_modify_time} =  Execute Command  stat -c %X ./textfiles/test_file.txt
    Should Be True  ${current_time} > ${last_access_time}
    Should Be True  ${current_time} > ${last_modify_time}
    [Teardown]  Execute Command  rm -rf ./textfiles

Put Directory With SCP (all) And Preserve Time
    [Tags]  pybot
    ${current_time} =  Get Current Date  result_format=epoch  exclude_millis=True
    Put Directory  ${LOCAL TEXTFILES}  .  recursive=True  scp=ALL  scp_preserve_times=True
    ${last_access_time} =  Execute Command  stat -c %X ./textfiles
    ${last_modify_time} =  Execute Command  stat -c %X ./textfiles
    Should Be True  ${current_time} > ${last_access_time}
    Should Be True  ${current_time} > ${last_modify_time}
    Remote Directory Should Exist With Subdirectories  ./textfiles
    [Teardown]  Execute Command  rm -rf ./textfiles

*** Keywords ***
Remove Local Empty Directory And Remote Files
    OS.Remove Directory  ${LOCAL TEXTFILES}${/}empty
    Execute Command  rm -rf ./textfiles

Remove Local And Remote Directory With Square Brackets
    OS.Remove Directory  ${LOCAL TEXTFILES}${/}directory[1]
    Execute Command  rm -rf ./textfiles

Remote Directory Should Exist With Content
    [Arguments]  ${destination}
    SSH.File Should Exist  ${destination}/${TEST FILE NAME}
    SSH.File Should Exist  ${destination}/${FILE WITH NEWLINES NAME}
    SSH.File Should Exist  ${destination}/${FILE WITH SPECIAL CHARS NAME}
    SSH.File Should Not Exist  ${destination}/${FILE WITH NON-ASCII NAME}
    SSH.Directory Should Not Exist  ${destination}/${SUBDIRECTORY NAME}

Remote Directory Should Exist With Subdirectories
    [Arguments]  ${destination}
    SSH.File Should Exist  ${destination}/${TEST FILE NAME}
    SSH.File Should Exist  ${destination}/${FILE WITH NEWLINES NAME}
    SSH.File Should Exist  ${destination}/${FILE WITH SPECIAL CHARS NAME}
    SSH.File Should Not Exist  ${destination}/${FILE WITH NON-ASCII NAME}
    SSH.File Should Exist  ${destination}/${SUBDIRECTORY NAME}/${FILE WITH NON-ASCII NAME}

Create File With Colon Char In Its Name
    SSH.File Should Not Exist   ${COLON CHAR FILE}
    OS.Create File  ${COLON CHAR FILE}

Check And Remove Local Added Directory
    [Arguments]  ${destination}
    ${files_list} =  SSH.List Files In Directory  ${destination}
    List should contain value  ${files_list}  ${COLON CHAR FILE_NAME}
    [Teardown]  OS.Remove File  ${COLON CHAR FILE}

Check Folder Permissions
   [Arguments]    ${expected_permission}
   ${actual_permission}=  Execute Command  stat -c %a to_put${/}Folder3
   Should Be Equal As Integers  ${actual_permission}  ${expected_permission}  Folder has not expected permission ${expected_permission}:\t${actual_permission}
