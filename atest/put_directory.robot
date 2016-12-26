*** Settings ***
Force Tags      pybot   jybot
Resource        resources/sftp.robot
Suite Setup     Login As Valid User
Suite Teardown  Close All Connections
Library         OperatingSystem  WITH NAME  OS

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

Put Directory Using Relative Source
    [Setup]  SSH.Directory Should Not Exist  ${REMOTE TEST ROOT}
    Put Directory  ${CURDIR}${/}testdata${/}textfiles  ${REMOTE TEST ROOT}
    Remote Directory Should Exist With Content  ${REMOTE TEST ROOT}
    [Teardown]  Execute Command  rm -rf ${REMOTE TEST ROOT}

Put Directory Should Fail When Source Does Not Exists
    Run Keyword And Expect Error  There was no source path matching 'non-existing'.
    ...                           Put Directory  non-existing

*** Keywords ***
Remove Local Empty Directory And Remote Files
    OS.Remove Directory  ${LOCAL TEXTFILES}${/}empty
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
